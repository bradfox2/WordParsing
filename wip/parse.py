import inspect
import json
import os
import pprint
from fractions import Fraction
from idlelib import paragraph
from tkinter.ttk import Style
from zipfile import BadZipfile

import click
from docx import Document, styles

from wip.convert import save_as_docx

wsl_headings = set(['WSL1Bld','WSL1'])

#doc_path = save_as_docx(os.getcwd()+'\\8218200.doc')

def get_left_indent(paragraph):
    '''get left indent value for a paragraph'''
    if paragraph.paragraph_format.left_indent is not None:
        return paragraph.paragraph_format.left_indent
    s = paragraph.style
    while s:
        if s.paragraph_format.left_indent is not None:
            return(s.paragraph_format.left_indent)
        else:
            s =  s.base_style
    return 0

def get_first_line_indent(paragraph):
    '''get left indent value for a paragraph'''
    if paragraph.paragraph_format.first_line_indent is not None:
        return paragraph.paragraph_format.first_line_indent
    s = paragraph.style
    while s:
        if s.paragraph_format.first_line_indent is not None:
            return(s.paragraph_format.first_line_indent)
        else:
            s =  s.base_style
    return 0

def emu_to_inches(emu):
    return float(emu)/914400

class Node(object):
    def __init__(self, value, parent = None):
        self.parent = parent
        self.children = []
        self.value = value

    def __repr__(self):
        if not self.value:
            return str(None)
        return f'id: {self.value.id}, children: {[_.value.id for _ in self.children]}'

class Step(object):
    def __init__(self, id, paragraph):
        self.text = paragraph.text
        self.tab_count = self.count_tabs()
        self.id = id
        self.heading = paragraph.style.name
        self._paragraph = paragraph
        self.left_indent = get_left_indent(self._paragraph)
        self.first_line_indent = get_first_line_indent(self._paragraph)
        self.combined_indent = self.first_line_indent + self.left_indent
        
    def __repr__(self):
        return str(self.id)+":"+f'{self.tab_count}'+':'+self.heading+":"+self.text.replace('\t','')+"\n"
        
    def count_tabs(self):
        return self.text.count('\t')

def compare(last_node, node):
    
    print(node.value)

    if last_node.value is None:
        return 1

    #deeper
    last = emu_to_inches(get_left_indent(last_node.value._paragraph))
    
    if emu_to_inches(get_left_indent(node.value._paragraph)) < last + 0.0625/2 and emu_to_inches(get_left_indent(node.value._paragraph)) > last - 0.0625/2:
        return 0

    if get_left_indent(last_node.value._paragraph) < get_left_indent(node.value._paragraph):
        return 1
    
    #shallower
    else:
        d = 0
        while get_left_indent(last_node.value._paragraph) > get_left_indent(node.value._paragraph) and (last_node.parent.value.heading != 'WSL1' or node.value.heading == 'WSL1'):
            d -= 1
            if last_node.parent.value is not None:
                last_node = last_node.parent
            else:
                print(last_node.value.text)
                break
        return d

def parse_children(root_node, steps, compare):
    """ Parse list of steps into a parent/child node heirarchy. 
    
    Arguments:
        root_node {Node} -- Root node object from which all other nodes will be children.
        steps {list of Node} -- List of Nodes that are children of root node.
        compare {function} -- function that takes n and n + 1 nodes and will compare nodes to determine heirarchical depth.
    
    Returns:
        Node -- Root node with children. 
    """
    last_step = root_node
    
    while True:
        cur_step = Node(steps.pop())
        depth_delta = compare(last_step, cur_step)
        if depth_delta > 0: # going deeper
            last_step.children.append(cur_step)
            cur_step.parent = last_step
        elif depth_delta < 0:
            parent = last_step.parent
            for i in range(-depth_delta):
                if parent.parent is not None:
                    parent = parent.parent
            parent.children.append(cur_step)
            cur_step.parent = parent
        #elif is_top_level:
            #root_node.children.append(cur_step)
            #cur_step.oarent = root_node
        else:
            last_step.parent.children.append(cur_step)
            cur_step.parent = last_step.parent
        if len(steps) == 0:
            break

        last_step = cur_step
    
    return root_node

def print_steps(node, depth = 0):
    start_string = '\t' * depth
    print('{}{}'.format(start_string, node.value))
    for child in node.children:
        print_steps(child, depth = depth + 1)

def default(o):
    if type(o) is Node:
        key = ' '.join(o.value.text.split()) if o.value is not None else 'Root'
        has_children = len(o.children) > 0
        if has_children:
            return {key:o.children}
        return key

@click.command()
@click.option('--doc_path', help='Path to file for parsing.')
def run(doc_path):
    if not doc_path:
        raise ValueError("Need doc_path.")

    document = Document(doc_path)

    steps = [Step(idx, paragraph) for idx, paragraph in enumerate(document.paragraphs) if paragraph.style.name != 'Note' and paragraph.text.strip() != '']
    steps.reverse()

    root_node = parse_children(Node(None), steps, compare)
    print_steps(root_node)
    #file_name = os.path.basename(doc_path)

    with open('test.json','w') as f:
        json.dump(root_node, f, default=default)

    j = json.dumps(root_node, default=default)
    pprint.pprint(j)

if __name__ == "__main__":
    run()
