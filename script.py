import requests
from inputs import InputData
import json

inputs = InputData()
payload = json.dumps(inputs.__dict__)
print(payload)