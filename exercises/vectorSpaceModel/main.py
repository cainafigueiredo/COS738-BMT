if __name__ == "__main__":

    import os
    WORKDIR = os.path.dirname(os.path.abspath(__file__))

    import sys
    sys.path.append(WORKDIR)

    from utils.cfg import QueryProcessorConfig, InvertedListGeneratorConfig
    from src.queryProcessor import QueryProcessor
    from src.indexer import InvertedListGenerator

    # Query Processor
    QUERY_PROCESSOR_CFG_FILEPATH = os.path.normpath(f"{WORKDIR}/PC.CFG")

    queryProcessorCFG = QueryProcessorConfig(configPath = QUERY_PROCESSOR_CFG_FILEPATH)
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

    # Indexer
    INVERTED_LIST_CFG_FILEPATH = os.path.normpath(f"{WORKDIR}/GLI.CFG")
    
    invertedListCFG = InvertedListGeneratorConfig(configPath = INVERTED_LIST_CFG_FILEPATH)
    documentFilePathList = [os.path.abspath(path) for path in invertedListCFG["LEIA"]]
    invertedListFilePath = os.path.abspath(invertedListCFG["ESCREVA"])

    os.makedirs(os.path.dirname(invertedListFilePath), exist_ok = True)

    invertedListGenerator = InvertedListGenerator(
        documentFilePathList = documentFilePathList,
        invertedListFilePath = invertedListFilePath
    )

    # Putting all together
    queryProcessor.run()
    invertedListGenerator.run()