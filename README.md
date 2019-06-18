# Test project to parse word documents in Python.

## Testing
```bash
$ pytest #--uno_server_url UNOCONV Server --keep_files True to keep conversion files in Test dir
```

## Bert as a service startup 
- running w finetuned model from cr classification training
```bash
$ bert-serving-start -model_dir model/uncased_L-12_H-768_A-12/ -tuned_model_dir=model/classification_fine_tuning_test_1/ -ckpt_name="model.ckpt-343" -num_worker=1 -port 8190 -port_out 8191 -max_seq_len 100
```

## Pipeline

```bash
$ python wordparsing/pipeline/pipeline.py --commit True
```
(for testing purposes):
Creates a sqlite database in wordparsing/storage with TextPart, Embedding, and Model tables.  See wordparsing/storage/data_classes.py


## Word Doc parsing notes

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

