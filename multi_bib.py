import itertools
import xml.dom.minidom
import html

from zipfile import ZipFile
import os
import shutil
import json
import logging
logging.basicConfig(level=logging.INFO)

class DocumentFootnotes():
    """
    Extracts all zotero cited references from docx document footnotes.
    """

    UNZIP_PREFIX = "temp_unzipped_"

    def __init__(self, filename, citations_filename="citations.json"):
        self.filename = filename
        self.filename_base = filename.split(".")[0]
        self.references = []
        self.reference_urls = []
        self.citations_filename = citations_filename

    def extract_reference_keys(self):
        self._unzip()
        self._extract_reference_keys()
        self._cleanup()
        return self.references

    def export_citations(self):
        self._unzip()
        self._extract_citations()
        self._cleanup()
        logging.info(json.dumps(self.citations, ensure_ascii=False).encode('utf8'))
        with open(self.citations_filename, "w") as f:
            json.dump(self.citations, f, ensure_ascii=False)
            logging.info("written citations to {}".format(self.citations_filename))
        return self.citations

    def _unzip(self):
        z = ZipFile(self.filename)
        self.unzipped_directory = self.UNZIP_PREFIX + self.filename_base
        z.extractall(self.unzipped_directory)
        self.footnotes_filename = os.path.join(self.unzipped_directory, "word", "footnotes.xml")
        logging.debug("unzipping to {}".format(self.footnotes_filename))

    def _cleanup(self):
        shutil.rmtree(self.unzipped_directory)
        logging.debug("cleaned up directory: {}".format(self.unzipped_directory))

    def _extract_raw_citation(self, line):
        l = html.unescape(line)
        js = l[l.find("{"):l.find(" </w:instrText>")]
        x = eval(js) #!hack! TODO: parse json differently
        return x

    def _extract_citation(self, line):
        item= [item["itemData"] for item in self._extract_raw_citation(line)["citationItems"]][0]
        item["id"] = "Item-{}".format(item["id"])
        return item

    def _extract_uri(self, line):
        x = self._extract_raw_citation(line)
        uris = [item["uri"][0].replace(" ", "") for item in x["citationItems"]]
        return uris

    def _extract_type(self, line):
        x = self._extract_raw_citation(line)
        type = [item["itemData"]["type"].replace(" ", "") for item in x["citationItems"]]
        return type[0]

    def _extract_citations(self):
        parsed_xml = xml.dom.minidom.parse(self.footnotes_filename)
        pretty_xml_as_string = parsed_xml.toprettyxml().split("\n")
        relevant_lines = [line for line in pretty_xml_as_string if line.find("ADDIN ZOTERO_ITEM CSL_CITATION") > 0]
        citations = [self._extract_citation(line) for line in relevant_lines]
        self.citations = { item["id"]: item for item in citations}

    def _extract_reference_keys(self):
        parsed_xml = xml.dom.minidom.parse(self.footnotes_filename)
        pretty_xml_as_string = parsed_xml.toprettyxml().split("\n")
        relevant_lines = [line for line in pretty_xml_as_string if line.find("ADDIN ZOTERO_ITEM CSL_CITATION") > 0]
        urls = [self._extract_uri(line) for line in relevant_lines]
        chain = itertools.chain(*urls)
        self.reference_urls = list(chain)
        self.references = [ref.split("/")[-1] for ref in self.reference_urls]



def html2docx(inputfile, outputfile):
    os.system("")
    os.system("pandoc {} -s -o {}".format(inputfile, outputfile))




def main():
    filename = "zotero_sample.docx"

    footnotes = DocumentFootnotes(filename)
    footnotes.export_citations()
    keys = footnotes.extract_reference_keys()
    print(keys)



if __name__ == "__main__":
    main()