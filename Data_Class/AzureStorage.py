import requests
from xml.etree import ElementTree


def upload_file_to_blob_storage():

    # URL des Blob-Speichers und Container-Namen
    url = "https://batstorppnecmesprdclrs03.blob.core.windows.net/superdepotreporting-attachments"
    container_name = "superdepotreporting-attachments"

    # SAS-Token für den Zugriff auf den Blob-Speicher
    sas_token = "sp=racwdl&st=2023-03-01T13:54:27Z&se=2039-02-28T21:54:27Z&spr=https&sv=2021-06-08&sr=c&sig=eaUtdKd2%2F5W320pmME3B8FiCO4dGrznbBIvGywnIMtE%3D"

    # Name der hochzuladenden Datei und Pfad zu der Datei auf dem lokalen System
    filename = "de55Kunden.xlsx"
    local_file_path = "Data/de55Kunden.xlsx"

    # Lesen des Inhalts der Datei
    with open(local_file_path, "rb") as file:
        file_contents = file.read()

    # Konstruieren der URL für die API-Anforderung
    api_url = f"{url}/{filename}?{sas_token}"

    # Festlegen der Anforderungsheader
    headers = {
        "x-ms-blob-type": "BlockBlob",
        "Content-Type": "application/octet-stream",
    }

    # Senden der API-Anforderung
    response = requests.put(api_url, data=file_contents, headers=headers)

    # Überprüfen der API-Antwort auf Erfolg
    if response.status_code == 201:
        print(f"Die Datei {filename} wurde erfolgreich in den Blob-Speicher hochgeladen.")
    else:
        print(f"Beim Hochladen der Datei {filename} ist ein Fehler aufgetreten. Statuscode: {response.status_code}")


def showData():

    # URL des Blob-Speichers und Container-Namen
    url = "https://batstorppnecmesprdclrs03.blob.core.windows.net"
    container_name = "superdepotreporting-attachments"

    # SAS-Token für den Zugriff auf den Blob-Speicher
    sas_token = "sp=racwdl&st=2023-03-01T13:54:27Z&se=2039-02-28T21:54:27Z&spr=https&sv=2021-06-08&sr=c&sig=eaUtdKd2%2F5W320pmME3B8FiCO4dGrznbBIvGywnIMtE%3D"

    # Konstruieren der URL für die API-Anforderung
    api_url = f"{url}/{container_name}?restype=container&comp=list&{sas_token}"

    # Senden der API-Anforderung
    response = requests.get(api_url)

    # Überprüfen der API-Antwort auf Erfolg
    if response.status_code == 200:
        # Parsen der XML-Antwort, um die Liste der Dateinamen zu erhalten
        root = ElementTree.fromstring(response.content)
        file_list = [blob.find("Name").text for blob in root.find("{http://schemas.microsoft.com/windowsazure}Blobs").findall("{http://schemas.microsoft.com/windowsazure}Blob")]
        print("Liste der Dateien im Container:")
        for file in file_list:
            print(file)
    else:
        print(f"Beim Abrufen der Liste der Dateien ist ein Fehler aufgetreten. Statuscode: {response.status_code}")


#upload_file_to_blob_storage()
showData()