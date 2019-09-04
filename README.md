# Parsing Word Documents

## Overview
Project will fetch, convert, embed and store document embeddings in a database.  A Unoconv server is used for universal conversion and is provided as a passed URL parameter, or an auto-started Docker Container.  Embedding is performed via services specified in wordparsing/services/... .py.  The BERT-as-a-service project is used by default, but should be seperately started.  Embedded representations are stored in a sqlite database, along with embedding model details, originating text, and a unique tie back to the source record.

## How To Run

Recommend use of a virtual env:  
```bash 
$ python -m venv :virtual_environment_name
```
If desired, setup a .env file with the UNOCONV_URL environment variable set to a running Unoconv server. If this is not set a Docker container with this service will be automatically started and used.

Pipelines are specified to process documents(docs, for now) into a converted format(docx, for now).  Pipeline can be fed with files from a directory or a query that returns paths to files.

## Bert as a service startup

If desired to use BERT, the service is recommended to be started independently with a trained BERT model. Else it will be started with a pretrained model that must be referenced in config.BERT_MODEL_DIR.
 
- running with finetuned model from previous classification task training:
```bash
$ bert-serving-start -model_dir model/uncased_L-12_H-768_A-12/ -tuned_model_dir=model/classification_fine_tuning_test_1/ -ckpt_name="model.ckpt-343" -num_worker=1 -port 8190 -port_out 8191 -max_seq_len 100
```
or using a google model 

```bash
$ bert-serving-start -model_dir models/uncased_L-12_H-768_A-12/ -num_worker=1 -port 8190 -port_out 8191 -max_seq_len 100
```

### From the CLI

Example: Run a pipeline to convert files in a directory, committing to a database constructed at config.TEXT_DB_PATH. The database will be created if it does not exist.

```bash
$ python wordparsing/pipeline/directory_pipeline 
--from_files_dir ./docs 
--converted_files_dir ./converted 
--convert_from_type doc
--convert_to_type docx 
--parsed_file_directory ./parsed
--commit True
```

Converted documents are stored in converted_files_dir, and parsed json files are in parsed_file_directory.

The example for a Query based pipeline is simliar but requires additional environment variables to be set:
- NIMS_CONNECTION_STRING - Source database connetion string.
- SWMS_MEDIA_FILER_PATH - Filer mount that contains referenced files brought back from the query. 
- SWMS_MEDIA_USER_NAME - Filer login, if needed.
- SWMS_MEDIA_USER_PASSWORD - Filer password, if needed.

The project will make an attempt at mounting the filer with the specified parameters. Ran into issues with cross domain login WinOS errors, so this is not yet totally stable.

Additional the query file must be specified containing a single query string. Query needs to return a source database unique id tying the media records to external data, a file name, and a unique file source dbid in that order.  The file name will be joined with the specified filer path to access the documen file. Edit the swms_media_pipeline.py file, for now. 

## Testing
```bash
$ pytest # --keep_files True to keep conversion files in Test dir
```

## Unoconv service startup
- https://cloud.docker.com/u/bradfox2/repository/docker/bradfox2/unoconv
- If UNOCONV_URL is not defined in the environment, the preceeding docker image will be run.

## Pipelines

Creates a sqlite database at ./text.db with TextPart, Embedding, and Model tables.  See wordparsing/storage/data_classes.py

## Config Parameters
- TODO

## Word Doc parsing notes

~~To get the full left indent, we need to get the indents plus the tab stops, add these together.  Tabs in EMUs and indents are in EMUs:~~  Left indent variable alone appears to be sufficient.

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

