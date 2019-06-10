import inspect
import itertools
import json
import os
import pprint
from fractions import Fraction
from idlelib import paragraph
from pathlib import Path
from tkinter.ttk import Style
from zipfile import BadZipfile

import click
from docx import Document, styles

#exclude paragraphs from parsing with this type of style. Notes, Tables, etc.
parse_exclude_paragraph_styles = {'Note'}

wsl_headings = set(['WSL1Bld','WSL1'])

def get_left_indent(paragraph):
    """get left indent value for a paragraph
    
    Arguments:
        paragraph {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
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
    """get first line indent value for a paragraph
    
    Arguments:
        paragraph {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
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
    """English Metric Units(EMU) units to inches
    
    Arguments:
        emu {num}
    
    Returns:
        num 
    """
    return float(emu)/914400

class Node(object):
    """General node class for parent/child relationship building.
    
    Arguments:
        object {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    def __init__(self, value, parent = None):
        self.parent = parent
        self.children = []
        self.value = value

    def __repr__(self):
        if not self.value:
            return str(None)
        #return f'id: {self.value.id}, children: {[_.value.id for _ in self.children]}'
        return print_steps(self)

class Step(object):
    """A step in a document, where each paragraph represents a new step.
    
    Arguments:
        object {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
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
    """Compare 2 nodes to obtain place in heirarchy.
    
    Arguments:
        last_node {[type]} -- [description]
        node {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    
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
    """pretty print node family"""
    start_string = '\t' * depth
    print('{}{}'.format(start_string, node.value))
    for child in node.children:
        print_steps(child, depth = depth + 1)

def default(o):
    """default handler for a type that JSON system package cannot parse automatically. parent step as key, child steps as value
    """
    if type(o) is Node:
        key = ' '.join(o.value.text.split()) if o.value is not None else 'Root'
        has_children = len(o.children) > 0
        if has_children:
            return {key:o.children}
        return key


def create_document_nodes(doc_path):
    document = Document(doc_path)

    steps = [Step(idx, paragraph) for idx, paragraph in enumerate(document.paragraphs) if paragraph.style.name not in parse_exclude_paragraph_styles and paragraph.text.strip() != '']
    steps.reverse()

    root_node = parse_children(Node(None), steps, compare)
    return root_node

@click.command()
@click.option('--doc_path', help='Path to file for parsing.')
@click.option('--save_path', help='Directory to save parsed representation.')
def parse_doc(doc_path, save_path):
    if not doc_path:
        raise ValueError("Need doc_path.")

    file_path = Path(doc_path)
    save_dir = Path(save_path)
    save_dir.mkdir(exist_ok=True)
    
    if file_path.is_dir():
        files_0, files_1 = itertools.tee(file_path.glob('*.docx'))
        len_files = sum(1 for _ in files_0) 
        print('{} files for parse.'.format(len_files))
        for idx, file_ in enumerate(files_1):
            print('Converting file {} of {}'.format(idx+1, len_files))
            root_node = create_document_nodes(file_)
            with open(save_dir.joinpath(file_.stem + '.json'),'w') as f:
                json.dump(root_node, f, default=default)
        return True
    else:
        root_node = create_document_nodes(file_path)
        with open(save_dir.joinpath(file_path.stem + '.json'),'w') as f:
            json.dump(root_node, f, default=default)
        return True

    return None

#TODO:  Document information also returned in the JSON.
if __name__ == "__main__":
    parse_doc()
