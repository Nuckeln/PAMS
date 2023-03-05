import requests

# Set the SAS token and URL for the dev container
SASToken = "sp=racwdl&st=2023-03-01T13:54:22Z&se=2039-02-28T21:54:22Z&spr=https&sv=2021-06-08&sr=c&sig=S9%2BnXWjT3LbveUgLDFrqMNOPDpvcq3DB5JrZhznB3dY%3D"
URL = "https://batstorpdnecmesdevclrs03.blob.core.windows.net/superdepotreporting-attachments?sp=racwdl&st=2023-03-01T13:54:22Z&se=2039-02-28T21:54:22Z&spr=https&sv=2021-06-08&sr=c&sig=S9%2BnXWjT3LbveUgLDFrqMNOPDpvcq3DB5JrZhznB3dY%3D"

def upload_file_to_azure(file_path):
    # Open the file and read its contents
    with open(file_path, "rb") as file:
        file_data = file.read()

    # Set the headers for the request
    headers = {
        "x-ms-blob-type": "BlockBlob",
        "Content-Type": "application/octet-stream",
        "Content-Length": str(len(file_data)),
    }

    # Make the request to upload the file to Azure Blob Storage
    response = requests.put(URL, headers=headers, data=file_data)

    # Check the response status code and raise an exception if there was an error
    if not response.ok:
        raise Exception("Error uploading file to Azure Blob Storage: {}".format(response.text))

    # Print the URL of the uploaded file
    print("Uploaded file to: {}".format(URL))

# Example usage
upload_file_to_azure("Data/temp/123456789.pdf")
