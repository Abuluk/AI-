import requests

url = "http://localhost:8000/api/v1/items/ai-auto-complete-ws"
files = {'files': open('test.jpg', 'rb')}
response = requests.post(url, files=files)
print(response.status_code)
print(response.text)