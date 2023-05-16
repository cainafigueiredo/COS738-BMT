import os
SCRIPT_DIR = "/home/cainafpereira/UFRJ/COS738-BMT/exercises/vectorSpaceModel/src"
PROJECT_DIR = os.path.normpath(f"{SCRIPT_DIR}/..")

import sys
sys.path.append(PROJECT_DIR)

import pickle
import numpy as np
import pandas as pd
from typing import Text, List
from tqdm import tqdm
from utils.textProcessing import vectorizeText
from utils import log

class Searcher:
    def __init__(
        self,
        modelFilePath: Text, 
        queriesFilePath: Text,
        resultsFilePath: Text
    ) -> None:
        self.modelFilePath = modelFilePath
        self.queriesFilePath = queriesFilePath
        self.resultsFilePath = resultsFilePath
        self.model = None
        self.queries = None
        self.logger = log.initLogger("SEARCHER")

    def loadModel(self):
        model = pickle.load(open(self.modelFilePath, "rb"))
        return model
    
    def loadQueries(self):
        queries = pd.read_csv(self.queriesFilePath, sep = ";")
        return queries  
    
    def searchFromQuery(self, query: Text, limit = -1):
        queryTerms = vectorizeText(query)
        queryTerms = list(pd.Series(queryTerms).unique())
        queryTerms = self.model.filterQueryTerms(queryTerms)
        similarities = []
        for queryTerm in queryTerms:
            documentIDs = self.model.filterDocumentsByQueryTerms(queryTerms)
            for documentID in documentIDs:
                weightQueryTermInDocumentID = self.model.getWeight(documentID, queryTerm, normalized = True)
                similarities.append([documentID, weightQueryTermInDocumentID**2])
        similarities = pd.DataFrame(data = similarities, columns = ["documentID", "similarity"])
        similarities.similarity = similarities.similarity.apply(np.sqrt)
        similarities = similarities.sort_values("similarity", ascending = False).reset_index(drop = True)
        similarities["rank"] = similarities.index + 1
        if limit > 0:
            similarities = similarities.iloc[:limit]
        return similarities

    def runQueries(self, limit = -1):
        results = []
        for i in tqdm(self.queries.index, desc = "Running queries..."):
            row = self.queries.loc[i]
            query = row.queryText
            number = row.queryNumber
            queryResults = self.searchFromQuery(query, limit = limit)
            queryResults["queryNumber"] = number
            queryResults = queryResults[["queryNumber", "rank", "documentID", "similarity"]]
            results.append(queryResults)
        results = pd.concat(results)
        return results

    def _run(self):
        self.model = log.executeFunction(
            logger = self.logger, 
            onStartMessage = "Loading model",
            onFinishMessage = "Model was loaded with success",
            onErrorMessage = "Error while loading model",
            func = self.loadModel
        )

        self.queries = log.executeFunction(
            logger = self.logger, 
            onStartMessage = "Loading queries",
            onFinishMessage = "Queries were loaded with success",
            onErrorMessage = "Error while loading queries",
            func = self.loadQueries
        )
        self.logger.info(f"Total Queries: {self.queries.shape[0]}")

        results = log.executeFunction(
            logger = self.logger, 
            onStartMessage = "Running queries",
            onFinishMessage = "All queries were executed with success",
            onErrorMessage = "Error while running queries",
            func = self.runQueries,
        )

        self.logger.info("Storing results")
        results.to_csv(self.resultsFilePath, index = False, sep = ";")
        self.logger.info("Results were stored with success")

    def run(self):
        log.executeModule(self.logger, self._run)