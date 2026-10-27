import os
import requests

# Replace this with your API Gateway endpoint
url = os.environ.get("API_URL", "https://your-api-id.execute-api.ap-southeast-2.amazonaws.com/prod/resource")

# If your API requires an API key or headers, add them here
headers = {
    "Content-Type": "application/json",
    # "x-api-key": "your-api-key",   # uncomment if required
}

# Example request body (only needed for POST/PUT)
payload = {
    "message": "Hello from client!"
}

try:
    response = requests.post(url, json=payload, headers=headers)

    print("Status Code:", response.status_code)
    print("Response Body:", response.text)

except requests.exceptions.RequestException as e:
    print("Error:", e)
