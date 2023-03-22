import dask
import json
import requests
from pathlib import Path
from logging import Logger
from bs4 import BeautifulSoup
from dask.diagnostics import ProgressBar


class Downloader:

    base_url = 'http://stimmdb.coli.uni-saarland.de'
    max_speaker_id = 2742
    session = requests.Session()

    def __init__(self, out_path: str, refetch_links: bool, logger: Logger):
        self.logger = logger
        self.out_path = out_path
        self.refetch_links = refetch_links
        self.links_file = f"{out_path}/data.json"

    def run(self):
        self.logger.info("Running downloader")
        self.logger.info(f"Saving at: {self.out_path}")
        if not Path(self.links_file).is_file() or self.refetch_links:
            self.logger.info("Saving file links")
            self.save_all_file_links()
        with open(self.links_file, "r") as links_file:
            data = json.load(links_file)
        self.download_data(data)

    def download_data(self, data):
        jobs = []
        self.logger.info("Setting up download jobs")
        for key, row in data.items():
            if row is not None:
                gender = row["gender"]
                classification = row["classification"]
                for file in row["files"]:
                    job = self.download_file(
                        key=key,
                        gender=gender,
                        classification=classification,
                        file=file
                    )
                    jobs += [job]
        self.logger.info("Downloading files")
        with ProgressBar():
            dask.compute(*jobs)

    @dask.delayed
    def download_file(self, key, gender, classification, file):
        data_path = f"{self.out_path}/{classification}/{gender}/{key}"
        Path(data_path).mkdir(parents=True, exist_ok=True)
        file_id = file.split("=")[1]
        file_path = f"{data_path}/{file_id}.wav"
        doc = requests.get(file)
        with open(file_path, 'wb') as f:
            f.write(doc.content)

    def save_all_file_links(self):
        session = self.db_session()
        ids = list(range(self.max_speaker_id))
        pages = [
            f"http://stimmdb.coli.uni-saarland.de/details.php4?SprecherID={number}"
            for number in ids
        ]
        jobs = [self.extract_links_from_page(session, page) for page in pages]
        with ProgressBar():
            data = dict(zip(ids, dask.compute(*jobs)))
        Path(self.links_file).parent.mkdir(exist_ok=True, parents=True)
        with open(self.links_file, "w") as link_file:
            json.dump(data, link_file, indent=4)

    @dask.delayed
    def extract_links_from_page(self, session, url):
        response = session.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        gender = self.get_gender(soup.find("div", class_="title").text)
        valid_classifications = ["healthy", "pathological"]
        data = {
            "page": url,
            "gender": gender,
        }
        for sess in soup.findAll('table', class_="sessiondetails"):
            classification = self.identify_classification(sess)
            data["classification"] = classification
            if classification in valid_classifications:
                data["files"] = self.get_file_links(sess)
                return data
            else:
                self.logger.warn(
                    f"Invalid classification(={classification}) found at url: {url}")

    def db_session(self):
        session = requests.Session()
        session.post(self.base_url, data={
                     'sb_search': 'Datenbankanfrage', 'sb_lang': 'English'})
        session.post(self.base_url, data={'sb_sent': 'Accept'})
        return session

    def identify_classification(self, sess):
        row = sess.find("tr", class_="detailsactive")
        classification = row.find_all("td")[1].text
        return classification

    def get_file_links(self, sess):
        files = sess.find_all("a", attrs={"target": "PLAY"})
        file_links = [f"{self.base_url}/{x.get('href')}" for x in files]
        return file_links

    def get_gender(self, title: str):
        title = title.lower()
        if "female" in title:
            return "female"
        if "male" in title:
            return "male"
        return "unknown"
