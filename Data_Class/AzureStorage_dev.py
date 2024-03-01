import requests
import xml.etree.ElementTree as ET
import pandas as pd
import uuid
from io import BytesIO

def get_blob_list_dev():
    SAS_TOKEN = "sp=racwdl&st=2023-03-01T13:54:22Z&se=2039-02-28T21:54:22Z&spr=https&sv=2021-06-08&sr=c&sig=S9%2BnXWjT3LbveUgLDFrqMNOPDpvcq3DB5JrZhznB3dY%3D"
    CONTAINER_URL = "https://batstorpdnecmesdevclrs03.blob.core.windows.net/superdepotreporting-attachments"

    # Make a request to the container to get the list of blobs
    response = requests.get(CONTAINER_URL + "?restype=container&comp=list&" + SAS_TOKEN)

    filesImSpeicher = []
    # Parse the XML response to get the list of blob names
    if response.status_code == 200:
        xml = response.text
        root = ET.fromstring(xml)
        for blob in root.findall(".//Blob"):
            # add the blob name to the list
            filesImSpeicher.append(blob.find("Name").text)

    return filesImSpeicher

def get_file_dev(name):
    SAS_TOKEN = "sp=racwdl&st=2023-03-01T13:54:22Z&se=2039-02-28T21:54:22Z&spr=https&sv=2021-06-08&sr=c&sig=S9%2BnXWjT3LbveUgLDFrqMNOPDpvcq3DB5JrZhznB3dY%3D"
    CONTAINER_URL = "https://batstorpdnecmesdevclrs03.blob.core.windows.net/superdepotreporting-attachments"
    
    # Create the blob URL
    blob_url = CONTAINER_URL + "/" + name + "?" + SAS_TOKEN
    
    # Make a request to the blob URL to get the blob content
    response = requests.get(blob_url)
    
    # Save the blob content to a object
    blob_content = response.content
    #return as object
    return blob_content


