import itertools
import xml.dom.minidom
import html

from zipfile import ZipFile
import os
import shutil

class DocumentFootnotes():
    """
    Extracts all zotero cited references from docx document footnotes.
    """

    UNZIP_PREFIX = "temp_unzipped_"

    def __init__(self, filename):
        self.filename = filename
        self.filename_base = filename.split(".")[0]
        self.references = []
        self.reference_urls = []

    def extract_reference_keys(self):
        self._unzip()
        self._extract_zotero_lines()
        self._cleanup()
        return self.references

    def _unzip(self):
        z = ZipFile(self.filename)
        self.unzipped_directory = self.UNZIP_PREFIX + self.filename_base
        z.extractall(self.unzipped_directory)
        self.footnotes_filename = os.path.join(self.unzipped_directory, "word", "footnotes.xml")

    def _cleanup(self):
        shutil.rmtree(self.unzipped_directory)

    def _extract_uri(self, line):
        l = html.unescape(line)
        js = l[l.find("{"):l.find(" </w:instrText>")]
        x = eval(js)
        uris = [item["uri"][0].replace(" ", "") for item in x["citationItems"]]
        return uris

    def _extract_zotero_lines(self):
        parsed_xml = xml.dom.minidom.parse(self.footnotes_filename)
        pretty_xml_as_string = parsed_xml.toprettyxml().split("\n")
        relevant_lines = [line for line in pretty_xml_as_string if line.find("ADDIN ZOTERO_ITEM CSL_CITATION") > 0]
        urls = [self._extract_uri(line) for line in relevant_lines]
        chain = itertools.chain(*urls)
        self.reference_urls = list(chain)
        self.references = [ref.split("/")[-1] for ref in self.reference_urls]




def get_reference_keys(docx_file):
    document_footnotes = DocumentFootnotes(docx_file)
    return document_footnotes.references


def html2docx(inputfile, outputfile):
    os.system("")
    os.system("pandoc {} -s -o {}".format(inputfile, outputfile))


from pyzotero import zotero
import yaml

from settings import *

class APIDownloader():
    def __init__(self, *refence_keys):

        self.zot = zotero.Zotero(library_id, library_type, api_key)
        self.refence_keys = refence_keys

        with open("config.yml", 'r') as yamlfile:
            config = yaml.load(yamlfile)
            self.tags = config.get("tags")

        print(self.tags) ##TODO add logger

        self.output_filename = "bibliography.html"  # TODO fix hardcoded

    def download_bib(self):

        with open(self.output_filename, "w") as f:
            f.write("<h1>Bibliography</h1>")

        if len(self.refence_keys) < 50:

            #TODO: single request; fix code in pyzotero to support multiple tags
            for tag in self.tags:
                self.process_single_batch(self.refence_keys, tag)

        else:
            print("TODO! implement repetitive calls")  ##TODO fix

        html2docx(self.output_filename, self.output_filename.split(".")[0] + ".docx")
        print("done!")

    def process_single_batch(self, keys, tag):

        # format=bib; style = filename of any style given on https://www.zotero.org/styles
        bib = self.zot.items(itemKey=",".join(keys), format="bib", tag=tag)
        bib_items = self.zot.items(itemKey=",".join(keys), tag=tag)
        retrieved_keys = [item["data"]["key"] for item in bib_items]
        lines = bib.split("\n")
        lines[0] = "<h2>{tag}</h2>".format(tag=tag)
        result = "\n".join(lines)
        print("keys for {tag} : {keys}".format(tag=tag, keys=retrieved_keys))
        with open(self.output_filename, "a") as f:
            f.write(result)



def main():
    filename = "zotero_sample.docx"

    footnotes = DocumentFootnotes(filename)
    keys = footnotes.extract_reference_keys()

    print(keys)

    downloader = APIDownloader(*keys)
    downloader.download_bib()


if __name__ == "__main__":
    main()