import requests

url = "http://localhost:8000/api/resume/upload"
data = {'role': 'Intern'}
files = {'file': open("../Resumes/resume.pdf", "rb")}

response = requests.post(url, data=data, files=files)

print("Status Code:", response.status_code)
print(response.json())
