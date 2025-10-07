# Project Nexus Python Client (skeleton)

This folder contains a minimal Python client skeleton for the Project Nexus core API.

Install locally for development:

```bash
python -m pip install -e sdk/python-client
```

Usage example:

```py
from pnexus_client import ProjectNexusClient

client = ProjectNexusClient(token='YOUR_TOKEN')
resp = client.get_buildings(page=1, size=10)
print(resp)
```
