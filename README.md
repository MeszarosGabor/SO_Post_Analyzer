# SO_Post_Analyzer
Utility functions and analyzer tools around StackOverflow Post dumps.


# SETUP
## Extract the xml source (not included)

## Set Pythonpath to directory root
Run from the directory root:
```
export PYTHONPATH=$PYTHONPATH:.
```

## Install Dependencies

```
$pip install -r requirements.txt
```

## Generate Import Collection

You may start with the parsing of the raw xml file and generate a python files metadata json file.
```
 python generate_import_collection.py -i test_xmls/SmallPost.xml -m metadata.jsonl -o out.jsonl
```

In case you already have a JSON file generated, you may opt out of the first step.

```
 python generate_import_collection.py -j <python_posts.jsonl> -o out.jsonl
```

The output file will be a jsonl file, with the following JSON content on every line:
```
{
    "id": "802",
    "imports": ["MySQLdb"],
    "date": "2008-08-03T20:07:05.290",
    "codes": <list of code snippets>}
```

## Generate First Appearances

Once the import collection is generated, the first appearances script collects the timestamps the individual libraries as well as pairs of libraries were imported the first time.
```
python generate_first_appearances_files.py -i <input jsonl> -o <output.json>
```


### Output format:

Individual:
```
{
    "MySQLdb": "2008-08-03",
}
```

Pairs:
```
{
    "parameterized|unittest": "2008-08-28",
}
```