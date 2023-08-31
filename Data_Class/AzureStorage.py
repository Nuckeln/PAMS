import requests
import xml.etree.ElementTree as ET
import pandas as pd
import uuid
import streamlit as st
from Data_Class.SQL import SQL_TabellenLadenBearbeiten as sql


def upload_file_to_blob_storage(filename, file_object, herkunft):
    '''Hochladen einer Datei in den Blob-Speicher. erwartet den Dateinamen, den Dateipfad und die Herkunft/Anwendung der Datei'''

    # URL des Blob-Speichers und Container-Namen
    url = "https://batstorppnecmesprdclrs03.blob.core.windows.net/superdepotreporting-attachments"
    container_name = "superdepotreporting-attachments"
    filenameorg = filename
    #add date as tt.mm.jjjj and _ and Time as hh.mm.ss to filename
    filenameorg = pd.Timestamp.now().strftime("%d_%m_%Y_%H_%M_%S") + '_' + filename
    # SAS-Token für den Zugriff auf den Blob-Speicher
    sas_token = "sp=racwdl&st=2023-03-01T13:54:27Z&se=2039-02-28T21:54:27Z&spr=https&sv=2021-06-08&sr=c&sig=eaUtdKd2%2F5W320pmME3B8FiCO4dGrznbBIvGywnIMtE%3D"
    filename = uuid.uuid4()

    # Lesen des Inhalts der Datei
    # with open(file_object, "rb") as file:
    #     file_contents = file.read()

    # Konstruieren der URL für die API-Anforderung
    api_url = f"{url}/{filename}?{sas_token}"

    # Festlegen der Anforderungsheader
    headers = {
        "x-ms-blob-type": "BlockBlob",
        "Content-Type": "application/octet-stream",
    }

    # Senden der API-Anforderung
    response = requests.put(api_url, data=file_object, headers=headers)
    print(response)

    # Überprüfen der API-Antwort auf Erfolg
    if response.status_code == 201:
        print(f"Die Datei {filename} wurde erfolgreich in den Blob-Speicher hochgeladen.")
    else:
        print(f"Beim Hochladen der Datei {filename} ist ein Fehler aufgetreten. Statuscode: {response.status_code}")

    #create a pandas dataframe with the filename and the filenameorg uploadedtime und user und Datum
    user = st.session_state.user
    df = pd.DataFrame({'filename': [filename], 'filenameorg': [filenameorg], 'user': [user], 'anwendung':herkunft, 'dateTime': [pd.Timestamp.now()]})
    #sql.sql_createTable('AzureStorage',df2)
    #sql.sql_createTable('AzureStorage',df)
    sql.addtoTable('AzureStorage',df)
    return filename

def get_blob_list():
    SAS_TOKEN = "sp=racwdl&st=2023-03-01T13:54:27Z&se=2039-02-28T21:54:27Z&spr=https&sv=2021-06-08&sr=c&sig=eaUtdKd2%2F5W320pmME3B8FiCO4dGrznbBIvGywnIMtE%3D"
    CONTAINER_URL = "https://batstorppnecmesprdclrs03.blob.core.windows.net/superdepotreporting-attachments"

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

def get_blob_file(name):
    SAS_TOKEN = "sp=racwdl&st=2023-03-01T13:54:27Z&se=2039-02-28T21:54:27Z&spr=https&sv=2021-06-08&sr=c&sig=eaUtdKd2%2F5W320pmME3B8FiCO4dGrznbBIvGywnIMtE%3D"
    CONTAINER_URL = "https://batstorppnecmesprdclrs03.blob.core.windows.net/superdepotreporting-attachments"

    # Create the blob URL
    blob_url = CONTAINER_URL + "/" + name + "?" + SAS_TOKEN
    
    # Make a request to the blob URL to get the blob content
    response = requests.get(blob_url)
    print(response)

    # Return the blob content as a file object
    if response.status_code == 200:
        return response.content

def lösche_blob_files():
    SAS_TOKEN = "sp=racwdl&st=2023-03-01T13:54:27Z&se=2039-02-28T21:54:27Z&spr=https&sv=2021-06-08&sr=c&sig=eaUtdKd2%2F5W320pmME3B8FiCO4dGrznbBIvGywnIMtE%3D"
    CONTAINER_URL = "https://batstorppnecmesprdclrs03.blob.core.windows.net/superdepotreporting-attachments"

    # Create the blob URL
    blob_url = CONTAINER_URL + "?" + SAS_TOKEN

    # Get the list of blobs in the container
    response = get_blob_list()

    # Delete each blob in the container
    for blob in response:
        delete_blob_url = blob_url + "/" + blob
        response = requests.delete(delete_blob_url)
        print(response)
    
def st_Azure_downloadBtn():
    '''erstellt einen Download Button für die Dateien mit Selectbox im Blob Storage'''
    sel_Datei = st.selectbox('Dateien auswählen', get_blob_list())
    file = get_blob_file(sel_Datei)
    print(sel_Datei)
    if st.download_button('Download', file, sel_Datei):
        st.success('Download erfolgreich')

def st_Azure_uploadBtn(herkunft):
    '''erstellt ein St.FileUploader und einen Upload Button für den Blob Storage erwartet die Herkunft/Anwendung der Datei'''
    file = st.file_uploader('Datei hochladen')
    filename = ''
    if st.button('Upload'):
        if file is not None:
            filename = upload_file_to_blob_storage(file.name, file, herkunft)
            st.success('Upload erfolgreich')
        else:
            st.error('Keine Datei ausgewählt')
    return filename

def st_Azure_deleteBtn():
    '''erstellt einen Delete Button für den Blob Storage'''
    if st.button('Delete'):
        lösche_blob_files()
        st.success('Delete erfolgreich')

