# Zotero multiple bibliographies workaround

### Attempt of a tool/workaround taking as input:

1. one or more microsoft word (.docx only) documents
2. a configuration file with a list of desired sections containing a list of Zotero assigned tags

### and giving as output:

One resulting bibliography document containing a categorised bibliography:

- section1 (e.g. primary sources)
    - item A
    - item B
- section2 (e.g. secondary sources)
    - item C
    - item D

whereby all items have actually been cited in one of the input documents.

## Stability

WORK IN PROGRESS. Bugs are likely.

## Requirements

- Python 3
- pandoc (optional)

installation:

```bash
pip install -r requirements.txt
```

## Setup

### Configure `settings.py`:

```
cp settings.py.sample settings.py
```

then edit the file by adding: 

- Your zotero **personal library ID** and your **API key** , which can be found [here](https://www.zotero.org/settings/keys) (you'll need to gnerate an API key), in the section `Your userID for use in API calls`


### Configure `config.yml`

- Choose a style using e.g. <http://editor.citationstyles.org> or leave the default
- Define a path to input files to be read
- Define the sections that you want.
    - for each section, add a list of zotero tags (e.g. `my tag1`) or itemTypes (e.g. `journalArticle`) 
    - if there is overlap, you'll get a section "duplicates" in the output - it'll be up to you to adapt the tags in the sections or on the items in zotero.
- run `python bibliography.py` and inspect the output of bibliography.html or (if you have pandoc installed) bibliography.docx
- by default some information is cached for 5 minutes. Adapt `cache_duration_in_minutes` inside the config.yml to your needs.



## optional alternative to explore as a developer 

WARNING: not supported yet

instead of making api calls to zotero to get formatted bibliographies, one could also use citeproc-js directly.

Download with:

```
# for formatting citations in a certain style
hg clone http://bitbucket.org/fbennett/citeproc-js/
cd citeproc-js
hg clone https://bitbucket.org/bdarcus/csl-utils
git clone git://github.com/citation-style-language/locales.git locale
```

make use of export of citations to json

```
from footnotes_extractor import DocumentFootnotes
footnotes = DocumentFootnotes(filename)
footnotes.export_citations()
```

then use javascript to format those citations