import os
import ast
import numpy as np
import pandas as pd
import pickle

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = f"{SCRIPT_DIR}/.."

import sys
sys.path.append(PROJECT_DIR)

from typing import Any, Text, List, Dict
from xml.dom import minidom
from utils.textProcessing import textPreprocessingFunc
from nltk.tokenize import word_tokenize
from abc import ABC, abstractmethod

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
        self.documentsData = self.documentsData.dropna()

    def storeInvertedList(self):
        self.documentsData.to_csv(self.invertedListFilePath, index = False, sep = ";")

    def run(self):
        self.parseCorpus()
        self.storeInvertedList()
        self.preprocessDocuments()
        self.generateInvertedList()
        self.storeInvertedList()

class WeightCalculator(ABC):
    def __init__(self, invertedList):
        self.invertedList = invertedList
        self.documentIDs = self.getDocumentIDs()

    def getDocumentIDs(self):
        documentIDs = self.invertedList.documentIDList.apply(
            lambda document: list(document.index)
        ).explode().unique()
        return set(documentIDs)

    def getTermCountInDocument(self, documentID, term):
        termCount = self.invertedList.loc[term].documentIDList.loc[documentID].termCount
        return termCount

    def getDocumentCountForTerm(self, term):
        documentCount = self.invertedList.loc[term].documentCount
        return documentCount

    def calculateDocumentWeightLengths(self):
        documentWeights = {}
        for term in self.invertedList.index:
            documents = self.invertedList.loc[term].documentIDList
            for documentID in documents.index:
                weight = self.getWeight(documentID, term, normalized = False)
                if documentID in documentWeights.keys():
                    documentWeights[documentID] += weight**2
                else:
                    documentWeights[documentID] = weight**2
        documentWeights = {documentID: np.sqrt(sumSquaredWeights) for documentID, sumSquaredWeights in documentWeights.items()}
        return documentWeights

    @abstractmethod
    def weightFunction(self, documentID, term):
        pass

    def getWeight(self, documentID, term, normalized = False):
        if term not in self.invertedList.index:
            raise Exception(f"Invalid term: the term {term} does not exist.")
        if documentID not in self.documentIDs:
            raise Exception(f"Invalid document ID: the document {documentID} does not exist.")
        try:
            weight = self.weightFunction(documentID, term)
            if normalized:
                weight = weight/self.documentWeightLengths[documentID]
            return weight
        except:
            return 0

class StandardTFIDF(WeightCalculator):
    def __init__(self, invertedList):
        super(StandardTFIDF, self).__init__(invertedList)
        self.totalDocuments = self.calculateNumberOfDocuments()
        self.maxTermCount = self.calculateMaxTermCount()
        self.documentWeightLengths = self.calculateDocumentWeightLengths()

    def weightFunction(self, documentID, term):
        termCount = self.getTermCountInDocument(documentID, term)
        documentCount = self.getDocumentCountForTerm(term)
        maxTermCount = self.maxTermCount
        totalDocuments = self.totalDocuments

        tf = termCount/maxTermCount
        idf = np.log(totalDocuments/documentCount)

        weight = tf*idf

        return weight

    def calculateNumberOfDocuments(self):
        documentsIDs = self.invertedList.documentIDList.apply(lambda document: document.index).explode().unique()
        totalDocuments = len(documentsIDs)
        return totalDocuments
    
    def calculateMaxTermCount(self):
        maxTermCount = self.invertedList.documentIDList.apply(lambda document: list(document.termCount)).explode().max()
        return maxTermCount

class TermDocumentMatrix:
    def __init__(self, invertedList: List[Dict], weightCalculator: WeightCalculator = StandardTFIDF):
        self.invertedList = invertedList
        self.weightCalculator = weightCalculator(invertedList)

    def getWeight(self, documentID, term, normalized = False):
        weight = self.weightCalculator.getWeight(documentID, term, normalized)
        return weight

class Indexer:
    def __init__(
        self, 
        invertedListFilePath: Text,
        indexesFilePath: Text
    ):
        self.invertedListFilePath = invertedListFilePath
        self.indexesFilePath = indexesFilePath

    def processInvertedList(self) -> pd.DataFrame:
        # Generating Statistics
        invertedList = pd.read_csv(self.invertedListFilePath, sep = ";").dropna()
        invertedList.documentIDList = invertedList.documentIDList.apply(ast.literal_eval)

        invertedList["documentCount"] = invertedList.documentIDList.apply(len)
        invertedList.documentIDList = invertedList.documentIDList.apply(
            lambda documents: pd.DataFrame(
                data = pd.Series(documents).value_counts().to_dict().items(),
                columns = ["documentID", "termCount"]
            ).set_index("documentID")
        )
        invertedList = invertedList.set_index("term")
        
        # Preprocessing the terms
        ## Filtering terms with only letters
        invertedList = invertedList[pd.Series(invertedList.index).apply(lambda term: term.isalpha()).values]

        ## Filtering terms with 2 or more letters
        invertedList = invertedList[(pd.Series(invertedList.index).apply(len) >= 2).values]

        ## Uppercasing terms
        invertedList.index = pd.Series(invertedList.index).apply(str.upper)

        return invertedList
    
    def createTermDocumentMatrix(self, invertedList):
        termDocumentMatrix = TermDocumentMatrix(invertedList = invertedList)
        pickle.dump(termDocumentMatrix, open(self.indexesFilePath, "wb"))

    def run(self):
        processedInvertedList = self.processInvertedList()
        self.createTermDocumentMatrix(processedInvertedList)