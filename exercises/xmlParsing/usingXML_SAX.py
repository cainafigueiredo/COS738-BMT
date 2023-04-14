from xml import sax

DATA_PATH = "../../data/CysticFibrosis2/cf79.xml"

class TitleHandler(sax.ContentHandler):
    def __init__(self) -> None:
        super().__init__()
        self.currentElement = ""
        self.titles = []

    def startElement(self, name, attrs):
        if name == "TITLE":
            self.currentElement = "TITLE"
            self.titles.append("")

    def endElement(self, name):
        if name == "TITLE":
            self.currentElement = ""

    def characters(self, content):
        if self.currentElement == "TITLE":
            self.titles[-1] += content

print("Parsing XML file and extracting titles...")
titlesHandler = TitleHandler()
parser = sax.make_parser()
parser.setContentHandler(titlesHandler)
parser.parse(DATA_PATH)
titles = titlesHandler.titles

print("Writing titles to a new XML file (titles.xml)...")
titlesElemText = "\n".join([f"<TITLE>{title}</TITLE>" for title in titles ])
newXMLContent = f"""<?xml version="1.0" encoding="UTF-8"?>
<TITLES>
{titlesElemText}
</TITLES>
"""
with open("titulo.xml", "w") as f:
    f.write(newXMLContent)

print("Done!")