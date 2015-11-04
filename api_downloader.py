from pyzotero import zotero
import yaml

from settings import *
import os
from time import time
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
        self.section_items = {section: [] for section in self.sections.keys()}
        self.section_items[DUPLICATES] = []
        self.section_items[NO_MATCH] = []

        logging.info("all keys: {}".format(citation_keys))

        self.bib_items_cache = ".cache.bib_items.p"
        self.bib_items_by_key_cache = ".cache.bib_items_by_key.p"
        self.tags_cache = ".cache.all_tags.p"
        self.cache_max_age = 300

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

            self.sections = {list(section.keys())[0]: list(section.values())[0] for section in sections}
            self.section_keys = [list(section.keys())[0] for section in sections]
            logging.info("all sections: {}".format(self.sections))

    def download_data(self):
        logging.info("reading bibliography/tag info from zotero API")
        by_chunks = list(self.chunks(self.citation_keys))
        logging.info("split keys into {} chunks".format(len(by_chunks)))
        for keys in by_chunks:
            logging.info("processing chunk...{}".format(keys))
            itemKeys = ",".join(keys)
            bib_items = self.zot.items(itemKey=itemKeys)
            self.bib_items.extend(bib_items)
        self.bib_items_by_key = {item['key']: item for item in self.bib_items}

        self.all_tags = []
        for item in self.bib_items:
            self.all_tags.extend(list(self._tags(item)))
        self.all_tags = list(set(self.all_tags))
        self._write_cache()

    def _read_cache(self):
        logging.info("reading bibliography/tag info from file cache")
        self.bib_items = pickle.load(open(self.bib_items_cache, "rb"))
        self.bib_items_by_key = pickle.load(open(self.bib_items_by_key_cache, "rb"))
        self.all_tags = pickle.load(open(self.tags_cache, "rb"))

    def _write_cache(self):
        pickle.dump(self.bib_items_by_key, open(self.bib_items_by_key_cache, "wb"))
        pickle.dump(self.bib_items, open(self.bib_items_cache, "wb"))
        pickle.dump(self.all_tags, open(self.tags_cache, "wb"))

    def _is_cache_valid(self):
        if os.path.isfile(self.bib_items_by_key_cache):
            mod_time = os.path.getmtime(self.bib_items_by_key_cache)
            current_time = time()
            if (mod_time + self.cache_max_age) > current_time:
                return True
        return False

    def load_data(self):
        if self._is_cache_valid():
            self._read_cache()
        else:
            self.download_data()

    def _tags_by_key(self, key):
        return [i['tag'] for i in self.bib_items_by_key[key]['data']['tags']]

    def _tags(self, item):
        return set([i['tag'] for i in item['data']['tags']])

    def add_to_sections(self):
        for item in self.bib_items:
            found_sections = []
            for section, sectiontags in self.sections.items():

                tag_match = len(self._tags(item).intersection(set(sectiontags))) > 0
                type_match = item['data']['itemType'] in sectiontags
                if tag_match or type_match:
                    self.section_items[section].append(item)
                    found_sections.append(section)
            if len(found_sections) > 1:
                item[DUPLICATES] = found_sections
                self.section_items[DUPLICATES].append(item)
            if len(found_sections) == 0:
                self.section_items[NO_MATCH].append(item)

    def chunks(self, l, n = 50):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]


    def sort_by_author(self, list):
        list_filtered = [el for el in list if el['data']['creators']]
        logging.info("filtered {} vs full {}".format(len(list_filtered), len(list)))
        sorted_list = sorted(list_filtered, key=lambda x: x['data']['creators'][0].get('lastName', ""))
        # sorted_list.extend(list(set(list).difference(set(list_filtered))))
        #TODO: add missing elements!
        #TODO: do not chunk across authors
        return sorted_list

    def download_bib(self):

        with open(self.output_filename, "w") as f:
            f.write("<h1>{}</h1>\n".format(self.title))

        for section in self.section_keys:
            self._process_single_section(section)

        self._process_single_section(DUPLICATES)
        self._process_single_section(NO_MATCH)

        html2docx(self.output_filename, self.output_filename.split(".")[0] + ".docx")
        logging.info("done!")

    def _process_single_section(self, section):

        items = self.section_items[section]
        if not items:
            return

        items = self.sort_by_author(items)

        logging.info("processing section {}".format(section))
        with open(self.output_filename, "a") as f:
            all_keys = [item['key'] for item in items]
            by_chunks = list(self.chunks(all_keys))
            f.write("<h2>{}</h2>\n".format(section))
            logging.info("split keys into {} chunks".format(len(by_chunks)))
            for keys in by_chunks:
                bib = self.zot.items(itemKey=",".join(keys), format="bib", style=self.style)
                lines = bib.split("\n")
                result = "\n".join(lines[1:])  # remove first line containing xml header
                logging.info(lines[1:3])
                f.write(result)
            additional_lines = self._handle_duplicates_no_matches(section, items)
            f.write("\n".join(additional_lines))

    def _handle_duplicates_no_matches(self, section, items):
        lines = []
        if section == DUPLICATES:
            lines.append("<h3>details:</h3>")
            for item in items:
                lines.append(
                    "ITEM FOUND IN SECTIONS: {} {}".format(item[DUPLICATES], item['data'].get('title', "NO_TITLE")))

        if section == NO_MATCH:
            lines.append("<h3>unused tags:</h3>")
            lines.append("<p>{}</p>".format(set(self.all_tags).difference(set(self.sections_all_tags))))
            lines.append("<h3>unused item types:</h3>")
            lines.append("<p>{}</p>".format(
                set([item['data'].get('itemType') for item in self.bib_items]).difference(set(self.sections_all_tags))))
        return lines


def main():
    keys = ['EJKZKRA2', 'TQJISAPU', 'T2KQXCMQ']

    downloader = APIDownloader(keys)

    downloader.load_data()
    downloader.add_to_sections()
    downloader.download_bib()


if __name__ == "__main__":
    main()
