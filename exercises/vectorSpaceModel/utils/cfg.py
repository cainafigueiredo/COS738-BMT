import re
import pandas as pd
from typing import Text

class ConfigBase:
    def __init__(self, configPath: Text):
        self.configPath = configPath
        self.cfg = None
        self.requiredInstructions = []
        self.loadConfig()
    
    def checkRequiredInstructions(self) -> bool:
        if self.cfg is not None:
            instructions = set(self.cfg.keys())
            if len(set(self.requiredInstructions) - instructions) == 0:
                return True
        return False

    def loadConfig(self) -> None:
        try:
            self.cfg = dict(
                re.findall(r"(.*)=(.*)", open(self.configPath).read())
            )

            hasAllRequiredInstructions = self.checkRequiredInstructions()
            if not hasAllRequiredInstructions:            
                raise Exception(f"Error while parsing config file. The following parameters are required: {', '.join(self.requiredInstructions)}")

        except Exception as e: 
            raise e
        
    def __getitem__(self, attr: Text) -> Text:
        if self.cfg is not None and attr in self.cfg.keys():
            return self.cfg[attr]
        
        raise Exception(f"Invalid param. {attr} is not specified in config file.")
    
class QueryProcessorConfig(ConfigBase):
    def __init__(self, configPath: Text):
        super().__init__(configPath)
        self.requiredInstructions = ["LEIA", "CONSULTAS", "ESPERADOS"]

class InvertedListGeneratorConfig(ConfigBase):
    def __init__(self, configPath: Text):
        super().__init__(configPath)
        self.requiredInstructions = ["LEIA", "ESCREVA"]

    def checkRequiredInstructions(self) -> bool:
        if self.cfg is not None:
            instructions = set(self.cfg.keys())
            if len(set(self.requiredInstructions) - instructions) == 0:
                if len(self.cfg["ESCREVA"]) == 1:
                    return True
        return False

    def loadConfig(self) -> None:
        try:
            cfg = re.findall(r"(.*)=(.*)", open(self.configPath).read())
            cfg = pd.DataFrame(data = cfg, columns = ["instruction", "value"])
            cfg = cfg.groupby("instruction").agg(lambda group: list(group))
            self.cfg = dict([*cfg.itertuples()])

            hasAllRequiredInstructions = self.checkRequiredInstructions()

            if not hasAllRequiredInstructions:            
                raise Exception(f"Error while parsing config file. The following parameters are required: {', '.join(self.requiredInstructions)}")

            self.cfg["ESCREVA"] = self.cfg["ESCREVA"][0]

        except Exception as e: 
            raise e
        
class IndexerConfig(ConfigBase):
    def __init__(self, configPath: Text):
        super().__init__(configPath)
        self.requiredInstructions = ["LEIA", "CONSULTAS"]