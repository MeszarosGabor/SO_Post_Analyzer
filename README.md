# SO_Post_Analyzer
Utility functions and analyzer tools around StackOverflow Post dumps.
Only posts with code content are considered!


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

## Generate Import Metadata

You may start with the parsing of the raw xml file and generate a python files metadata json file.
```
 python generate_extracted_import_metadata.py -i test_xmls/SmallPost.xml -m metadata.jsonl -o out.jsonl
```

In case you already have a JSON file generated, you may opt out of the first step.

```
 python generate_extracted_import_metadata.py -j <python_posts.jsonl> -o out.json
```

The output file will be a jsonl file, with the following JSON content on every line:
```
{
    "id": "802",
    "imports": ["MySQLdb"],
    "date": "2008-08-03T20:07:05.290",
    "codes": <list of code snippets>}
```

IMPORTANT! Every subsequent script will rely on this generated out.json content!

## Generate First Appearances and Appearance Count Statistics

Once the import metadata is generated, the `generate_indiv_and_pair_lib_stats` script collects the timestamps the individual libraries as well as pairs of libraries were imported the first time.
```
python generate_indiv_and_pair_lib_stats.py -i <input jsonl> -o <output.json>
```

### Output format:
The output contains 4 JSON files encoding the appearance count dictionaries of 
individual libraries as pairs (pairs are keyed in a canonical format: <LIB_A|LIB_B>, alphabetically ordered) as well as
the timestamps of the first appearances of the libs/pairs under the same keying.

Individual:
```
{
    "MySQLdb": 123,
}
```
and
```
{
    "MySQLdb": "2008-08-03",
}
```

Pairs:
```
{
    "parameterized|unittest": 23,
}
```
and 
```
{
    "parameterized|unittest": "2008-08-28",
}
```

## Generate Post Count to New Libs/Pairs Statistics

This script takes a time-sorted list of all posts and counts the number
of occurrences of unique posts and post pairs as functions of the number of post. The output file is a list of (x,y) values of the respectvei functions.


# UNDER THE HOOD... (ENG INTERNALS)

## Packages ignored
We generally ignore packages that are not listed on Pypi and are not part of
the Python built-in library list (checked for 2.7 and 3.12). An inclusion-list
is populated for a handful of exceptions such as `rest_framework`.

Notable (non-negligible hit count) ignored libraries include:
- `mpl_toolkits` (most likely a deprecated `matplotlib` internal)
