Test project to parse word documents in Python.

To get the full left indent, we need to get the indents plus the tab stops, add these together.  Tabs in EMUs and indents are in EMUs:

To get parent paragraph styles tabs stops:

document.paragraphs[26].style.base_style.paragraph_format.tab_stops

len(document.paragraphs[26].style.base_style.paragraph_format.tab_stops) 
>>> 5

To get indents:
document.paragraphs[0].paragraph_format.left_indent
then,
document.paragraphs[0].style.paragraph_format.left_indent
if none, then, get indents from parent styles through inheritance chain

indents give starting point, then count tabs 


## Testing
```bash
$ pytest #--uno_server_url UNOCONV Server --keep_files True to keep conversion files in Test dir
```