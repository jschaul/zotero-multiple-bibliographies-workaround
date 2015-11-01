# Zotero multiple bibliographies workaround

### Attempt of a tool/workaround taking as input:

1. one or more microsoft word (.docx only) documents
2. a configuration file with a list of desired tags matching Zotero assigned tags to references

### and giving as output:

One resulting bibliography document containing a categorised bibliography:

- tag1 (e.g. primary sources)
    - item A
    - item B
- tag2 (e.g. secondary sources)
    - item C
    - item D

whereby all items have actually been cited in one of the input documents.

## Stability

WORK IN PROGRESS. EXPERIMENTAL!

## Requirements

- Python 3
- installed pandoc tool

installation:

```bash
pip install -r requirements.txt


# for formatting citations in a certain style
hg clone http://bitbucket.org/fbennett/citeproc-js/
cd citeproc-js
hg clone https://bitbucket.org/bdarcus/csl-utils
git clone git://github.com/citation-style-language/locales.git locale
```

## Setup

- Choose a style using e.g. <http://editor.citationstyles.org>
