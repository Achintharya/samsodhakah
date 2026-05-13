import requests

url = "http://127.0.0.1:8000/api/documents/"
response = requests.get(url)

if response.status_code == 200:
    print(response.json())
else:
    print(f"Error: {response.status_code}, {response.text}")