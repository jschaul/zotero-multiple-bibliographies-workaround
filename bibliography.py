
import yaml
from api_downloader import APIDownloader
from footnotes_extractor import DocumentFootnotes

input_filenames = []

with open("config.yml", 'r') as yamlfile:
    config = yaml.load(yamlfile)
    input_filenames = config.get("input_filenames")


all_keys = []
for filename in input_filenames:
    footnotes = DocumentFootnotes(filename)
    all_keys.extend(footnotes.extract_reference_keys())


downloader = APIDownloader(all_keys)


downloader.load_data()
downloader.add_to_sections()
downloader.download_bib()


