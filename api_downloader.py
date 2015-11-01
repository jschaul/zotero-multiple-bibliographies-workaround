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
        bib = self.zot.items(itemKey=",".join(keys), format="bib", tag=tag, style="modern-humanities-research-association")
        bib_items = self.zot.items(itemKey=",".join(keys), tag=tag)
        retrieved_keys = [item["data"]["key"] for item in bib_items]
        lines = bib.split("\n")
        lines[0] = "<h2>{tag}</h2>".format(tag=tag)
        result = "\n".join(lines)
        print("keys for {tag} : {keys}".format(tag=tag, keys=retrieved_keys))
        with open(self.output_filename, "a") as f:
            f.write(result)


    #downloader = APIDownloader(*keys)
    #downloader.download_bib()
