import requests

url = "http://127.0.0.1:8000/api/drafting/section"
params = {
    "document_id": "cf8c47b8730d",
    "section_type": "related_work",
    "topic": "Machine Learning in Healthcare"
}

response = requests.post(url, params=params)

if response.status_code == 200:
    print(response.json())
else:
    print(f"Error: {response.status_code}, {response.text}")