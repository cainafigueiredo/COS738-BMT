import os
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = f"{SCRIPT_DIR}/.."

import sys
sys.path.append(PROJECT_DIR)

from typing import Text, List
from xml.dom import minidom
from utils.textProcessing import textPreprocessingFunc
from nltk.tokenize import word_tokenize

class InvertedListGenerator:
    def __init__(
            self, 
            documentFilePathList: List[Text],
            invertedListFilePath: Text
        ):
        self.documentFilePathList = documentFilePathList
        self.invertedListFilePath = invertedListFilePath
        self.documentsData = []

    def parseDocument(self, documentFilePath):
        dataDOM = minidom.parse(documentFilePath)

        data = []
        
        records = dataDOM.getElementsByTagName("RECORD")
        for record in records:
            recordNum = record.getElementsByTagName("RECORDNUM")[0].firstChild.data.strip()
            abstract = record.getElementsByTagName("ABSTRACT")
            extract = record.getElementsByTagName("EXTRACT")
            if abstract != []:
                abstract = abstract[0].firstChild.data
            elif extract != []:
                abstract = extract[0].firstChild.data
            else: 
                abstract = None
            
            data.append([recordNum, abstract])

        return data

    def parseCorpus(self):
        self.documentsData = []
        for documentFilePath in self.documentFilePathList:
            self.documentsData += self.parseDocument(documentFilePath)
        self.documentsData = pd.DataFrame(self.documentsData, columns = ["recordNum", "abstract"])

    def preprocessDocuments(self):
        self.documentsData = self.documentsData.dropna()
        self.documentsData["abstract"] = self.documentsData["abstract"].apply(textPreprocessingFunc)

    def generateInvertedList(self):
        self.documentsData["abstract"] = self.documentsData["abstract"].apply(
            lambda text: word_tokenize(text, language = "english", preserve_line = False)
        )
        self.documentsData = self.documentsData.explode("abstract")
        self.documentsData = self.documentsData.groupby("abstract").agg(lambda group: list(group)).reset_index()
        self.documentsData.columns = ["term", "documentIDList"]
        self.documentsData = self.documentsData.sort_values("term")

    def storeInvertedList(self):
        self.documentsData.to_csv(self.invertedListFilePath, index = False, sep = ";")

    def run(self):
        self.parseCorpus()
        self.storeInvertedList()
        self.preprocessDocuments()
        self.generateInvertedList()
        self.storeInvertedList()
