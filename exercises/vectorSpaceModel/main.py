import os
WORKDIR = os.path.dirname(os.path.abspath(__file__))

import sys
sys.path.append(WORKDIR)

from utils.cfg import QueryProcessorConfig, InvertedListGeneratorConfig, IndexerConfig, SearcherConfig
from utils import log
from src.queryProcessor import QueryProcessor
from src.indexer import InvertedListGenerator, Indexer
from src.searcher import Searcher

def main():
    # Init Loggers
    settingsLogger = log.initLogger("SETTINGS")

    # Loading Settings
    QUERY_PROCESSOR_CFG_FILEPATH = os.path.normpath(f"{WORKDIR}/PC.CFG")
    INVERTED_LIST_CFG_FILEPATH = os.path.normpath(f"{WORKDIR}/GLI.CFG")
    INDEXER_CFG_FILEPATH = os.path.normpath(f"{WORKDIR}/INDEX.CFG")
    SEARCHER_CFG_FILEPATH = os.path.normpath(f"{WORKDIR}/BUSCA.CFG")

    queryProcessorCFG = log.executeFunction(
        logger = settingsLogger,
        onStartMessage = "Loading query processor settings",
        onFinishMessage = "Query processor settings were loaded with success",
        logResults = True,
        func = QueryProcessorConfig(configPath = QUERY_PROCESSOR_CFG_FILEPATH).loadConfig
    )
    
    invertedListCFG = log.executeFunction(
        logger = settingsLogger,
        onStartMessage = "Loading inverted list generator settings",
        onFinishMessage = "Inverted list generator settings were loaded with success",
        logResults = True,
        func = InvertedListGeneratorConfig(configPath = INVERTED_LIST_CFG_FILEPATH).loadConfig
    )
    
    indexerCFG = log.executeFunction(
        logger = settingsLogger,
        onStartMessage = "Loading indexer settings",
        onFinishMessage = "Indexer settings were loaded with success",
        logResults = True,
        func = IndexerConfig(configPath = INDEXER_CFG_FILEPATH).loadConfig
    )

    searcherCFG = log.executeFunction(
        logger = settingsLogger,
        onStartMessage = "Loading searcher settings",
        onFinishMessage = "Searcher settings were loaded with success",
        logResults = True,
        func = SearcherConfig(configPath = SEARCHER_CFG_FILEPATH).loadConfig
    )

    # Query Processor
    queriesFilePath = os.path.abspath(queryProcessorCFG["LEIA"])
    processedQueriesFilePath = os.path.abspath(queryProcessorCFG["CONSULTAS"])
    expectedResultsFilePath = os.path.abspath(queryProcessorCFG["ESPERADOS"])

    os.makedirs(os.path.dirname(processedQueriesFilePath), exist_ok = True)
    os.makedirs(os.path.dirname(expectedResultsFilePath), exist_ok = True)

    queryProcessor = QueryProcessor(
        queriesFilePath = queriesFilePath,
        processedQueriesFilePath = processedQueriesFilePath, 
        expectedResultsFilePath = expectedResultsFilePath
    )

    # Inverted List   
    documentFilePathList = [os.path.abspath(path) for path in invertedListCFG["LEIA"]]
    invertedListFilePath = os.path.abspath(invertedListCFG["ESCREVA"])

    os.makedirs(os.path.dirname(invertedListFilePath), exist_ok = True)

    invertedListGenerator = InvertedListGenerator(
        documentFilePathList = documentFilePathList,
        invertedListFilePath = invertedListFilePath
    )

    ## Indexer  
    invertedListFilePath = os.path.abspath(indexerCFG["LEIA"])
    indexesFilePath = os.path.abspath(indexerCFG["ESCREVA"])

    os.makedirs(os.path.dirname(indexesFilePath), exist_ok = True)

    indexer = Indexer(
        invertedListFilePath = invertedListFilePath,
        indexesFilePath = indexesFilePath
    )

    ## Searcher   
    modelFilePath = os.path.abspath(searcherCFG["MODELO"])
    queriesFilePath = os.path.abspath(searcherCFG["CONSULTAS"])
    resultsFilePath = os.path.abspath(searcherCFG["RESULTADOS"])

    os.makedirs(os.path.dirname(resultsFilePath), exist_ok = True)

    searcher = Searcher(
        modelFilePath = modelFilePath, 
        queriesFilePath = queriesFilePath,
        resultsFilePath = resultsFilePath
    )

    # Putting all together
    queryProcessor.run()
    invertedListGenerator.run()
    indexer.run()
    searcher.run()

if __name__ == "__main__":
    # Logger
    logger = log.initLogger("MAIN")
    log.executeFunction(
        logger, 
        onStartMessage = "Welcome! The system has been started",
        onFinishMessage = "All done! The system has been finished", 
        onErrorMessage = "An error was found while executing the system",
        func = main
    )