from xml.dom import minidom

DATA_PATH = "../../data/CysticFibrosis2/cf79.xml"

print("Parsing XML file...")
data = minidom.parse("autores.xml")

print("Extracting authors...")
authorsElem = data.getElementsByTagName("author")
authors = [author.firstChild.data for author in authorsElem]

print("Writing authors to a new XML file (autores.xml)...")
authorsElemText = "\n".join([f"<AUTHOR>{author}</AUTHOR>" for author in authors ])
newXMLContent = f"""<?xml version="1.0" encoding="UTF-8"?>
<AUTHORS>
{authorsElemText}
</AUTHORS>
"""
with open("autores.xml", "w") as f:
    f.write(newXMLContent)

print("Done!")