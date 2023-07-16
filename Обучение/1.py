# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import requests
import json

url = "https://api.trello.com/1/boards/{id}/memberships"

headers = {
  "Accept": "application/json"
}

query = {
  'key': 'APIKey',
  'token': 'APIToken'
}

response = requests.request(
   "GET",
   url,
   headers=headers,
   params=query
)

print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
