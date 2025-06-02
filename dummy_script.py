import requests
import json

# Define the URL of your running Flask server
url = "http://127.0.0.1:5000/workflow"

# Sample input data
payload = {
    "question": "How can we optimize AI tool usage across departments?",
    "chat_history": [],
    "include_report_context": True
}

# Set headers
headers = {
    "Content-Type": "application/json"
}

# Send the POST request
response = requests.post(url, data=json.dumps(payload), headers=headers)

# Check response
if response.status_code == 200:
    print("✅ Chatbot Response:")
    print(json.dumps(response.json(), indent=2))
else:
    print(f"❌ Error {response.status_code}:")
    print(response.text)
