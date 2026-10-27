# API Test

Sends a test POST request to the team's AWS API Gateway endpoint and prints the status code and response, to check the cloud end of the pipeline is reachable.

## Run

```bash
pip install -r requirements.txt
export API_URL=https://<api-id>.execute-api.ap-southeast-2.amazonaws.com/prod/resource
python api_test.py
```

To send different data, edit `payload` in the script. If the endpoint needs an API key, uncomment the `x-api-key` header.
