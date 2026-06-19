
import requests


base_url = "http://localhost:8000"


def upload_documents(file_path:str) -> dict:
    upload_url = f"{base_url}/api/upload"
    with open(file_path, 'rb') as file:
        file = {'file': file}
        response = requests.post(upload_url, files=file)
    return response.json()

def get_response_from_rag(query:str) -> dict:
    rag_url = f"{base_url}/api/chat"
    payload = {"query": query}
    response = requests.post(rag_url, json=payload)
    return response.json()