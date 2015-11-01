from pyzotero import zotero
import yaml

from settings import *
import os
import itertools
import logging

logging.basicConfig(level=logging.INFO)

import pickle


def html2docx(inputfile, outputfile):
    os.system("")
    os.system("pandoc {} -s -o {}".format(inputfile, outputfile))

DUPLICATES = "duplicates"
NO_MATCH = "no_section_match"


class APIDownloader():
    def __init__(self, citation_keys, output_filename="bibliography.html",
                 style="modern-humanities-research-association"):
        self.zot = zotero.Zotero(library_id, library_type, api_key)
        self.citation_keys = citation_keys
        self.output_filename = output_filename
        self.style = style
        self.bib_items = []
        self.bib_items_by_key = {}
        self.all_tags = []

        self._parse_config()
        self.section_items = {section:[] for section in self.sections.keys()}
        self.section_items[DUPLICATES] = []
        self.section_items[NO_MATCH] = []

        logging.info("all keys: {}".format(citation_keys))

    def _parse_config(self):
        with open("config.yml", 'r') as yamlfile:
            config = yaml.load(yamlfile)

            self.style = config.get("style")
            self.output_filename = config.get("output_filename")
            self.title = config.get("title")

            sections = config.get("sections")
            tags = [list(section.values())[0] for section in sections]
            self.sections_all_tags = list(itertools.chain(*tags))
            logging.info("all section tags: {}".format(self.sections_all_tags))

            self.sections = {list(section.keys())[0]:list(section.values())[0] for section in sections}
            self.section_keys = [list(section.keys())[0] for section in sections]
            logging.info("all sections: {}".format(self.sections))

    def download_data(self):
        by_chunks = list(self.chunks(self.citation_keys, 50))
        logging.info("split keys into {} chunks".format(len(by_chunks)))
        for keys in by_chunks:
            logging.info("processing chunk...{}".format(keys))
            itemKeys = ",".join(keys)
            bib_items = self.zot.items(itemKey=itemKeys)
            self.bib_items.extend(bib_items)
        self.bib_items_by_key = {item['key']:item for item in self.bib_items}

        pickle.dump( self.bib_items_by_key, open( "bib_items_by_key.p", "wb" ) )
        pickle.dump( self.bib_items, open( "bib_items.p", "wb" ) )
        self.all_tags = self.zot.tags()
        pickle.dump( self.bib_items, open( "all_tags.p", "wb" ) )

    def load_data(self):
        self.bib_items = pickle.load( open( "bib_items.p", "rb" ) )
        self.bib_items_by_key = pickle.load( open( "bib_items_by_key.p", "rb" ) )
        self.all_tags = pickle.load( open( "all_tags.p", "rb" ) )

    def tags_by_key(self, key):
        return [i['tag'] for i in self.bib_items_by_key[key]['data']['tags']]

    def tags(self, item):
        return set([i['tag'] for i in item['data']['tags']])

    def itemType(self, item):
        return item['data']['itemType']

    def add_to_sections(self):

        for item in self.bib_items:
            found_sections = []
            for section, sectiontags in self.sections.items():
                tag_match = len(self.tags(item).intersection(set(sectiontags))) > 0
                type_match = self.itemType(item) in sectiontags
                if tag_match or type_match:
                    self.section_items[section].append(item)
                    found_sections.append(section)
            if len(found_sections) > 1:
                item[DUPLICATES] = found_sections
                self.section_items[DUPLICATES].append(item)
            if len(found_sections) == 0:
                self.section_items[NO_MATCH].append(item)


    def chunks(self, l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def download_bib(self):

        with open(self.output_filename, "w") as f:
            f.write("<h1>{}</h1>\n".format(self.title))

        for section in self.section_keys:
            self.process_single_section(section)

        self.process_single_section(DUPLICATES)
        self.process_single_section(NO_MATCH)

        html2docx(self.output_filename, self.output_filename.split(".")[0] + ".docx")
        logging.info("done!")

    def process_single_section(self, section):

        logging.info("processing section {}".format(section))

        with open(self.output_filename, "a") as f:
            items = self.section_items[section]
            all_keys = [item['key'] for item in items]
            by_chunks = list(self.chunks(all_keys, 50))
            f.write("<h2>{}</h2>\n".format(section))
            logging.info("split keys into {} chunks".format(len(by_chunks)))
            for keys in by_chunks:
                bib = self.zot.items(itemKey=",".join(keys), format="bib", style=self.style)
                lines = bib.split("\n")
                self._handle_duplicates_no_matches(lines, section, items)
                result = "\n".join(lines[1:]) # remove first line containing xml header
                logging.info(lines[1:])
                f.write(result)

    def _handle_duplicates_no_matches(self, lines, section, items):
        if section == DUPLICATES:
            lines.append("<h3>details:</h3>")
            for item in items:
                lines.append("ITEM FOUND IN SECTIONS: {} {}".format(item[DUPLICATES], item['data'].get('title', "NO_TITLE")))

        if section == NO_MATCH or section == DUPLICATES:
            lines.append("<h3>unused tags:</h3>")
            lines.append("<p>{}</p>".format(set(self.all_tags).difference(set(self.sections_all_tags))))
            lines.append("<h3>unused item types:</h3>")
            lines.append("<p>{}</p>".format(set([item['data'].get('itemType') for item in self.bib_items]).difference(set(self.sections_all_tags))))


def main():

    keys = ['EJKZKRA2', 'TQJISAPU', 'T2KQXCMQ']

    downloader = APIDownloader(keys)

    downloader.download_data()
    downloader.load_data()
    downloader.add_to_sections()
    downloader.download_bib()

if __name__ == "__main__":
    main()

