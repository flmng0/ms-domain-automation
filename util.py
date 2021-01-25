import requests
import os

# Constants
CACHE_PATH = f"/home/admtimda/ms-domain-automation/cache"
VERSION_FILE = f"{CACHE_PATH}/version.txt"

# O365 Constants
O365_PREFIX = "https://endpoints.office.com"

class Util():
    def __init__(self, client_id, instance="Worldwide", proxies=None):
        self.client_id = client_id
        self.instance = instance
        self.proxies = proxies

    # Check whether there were any updates
    def has_updates(self):
        # Construct the request URL
        request_url = f"{O365_PREFIX}/version?clientrequestid={self.client_id}"

        # Send the actual request
        data = requests.get(request_url, proxies=self.proxies).json()

        # Find the version for the requested instance
        obj = next(obj for obj in data if obj["instance"] == self.instance)
        latest_version = int(obj["latest"])

        # Create the directory for the version file if it doesn't already
        # exist
        base = os.path.dirname(VERSION_FILE)
        if not os.path.exists(base):
            os.makedirs(base)

        # Find the version that the endpoints were at the last time this
        # script was run.
        old_version = 0
        if os.path.isfile(VERSION_FILE):
            with open(VERSION_FILE, "r") as f:
                old_version = int(f.readline())

        updated = old_version < latest_version

        with open(VERSION_FILE, "w") as f:
            f.write(str(latest_version))

        return {
            "did_update": updated,
            "old_version": old_version,
        }

    # Collect all endpoints as a dictionary:
    #   endpoints {
    #       'ips': { '<serviceArea>': set with ips, '<serviceArea2>': ... },
    #       'urls': { '<serviceArea>': set with urls, '<serviceArea2>': ... },
    #   }
    def collect_endpoints(self):
        ips = {}
        urls = {}

        request_url = f"{O365_PREFIX}/endpoints/{self.instance}/?clientrequestid={self.client_id}&NoIPv6=true"
        data = requests.get(request_url, proxies=self.proxies).json()

        for obj in data:
            sa = obj['serviceArea']
            
            # Initialize the sets if they don't exist
            if not sa in ips: ips[sa] = set()
            if not sa in urls: urls[sa] = set()

            # If there are IPs listed in this endpoint, add them to the
            # `ips` set.
            if 'ips' in obj: 
                ips[sa] = ips[sa] | {ip for ip in obj['ips']}

            # If there are URLs listed in this endpoint, add them to the
            # `urls` set.
            if 'urls' in obj: 
                # FMC processes URLs by substring matching and doesn't
                # support traditional wildcard matching (*).
                urls[sa] = urls[sa] | {url.replace('*', '') for url in obj['urls']}
            
        return {
            'ips': ips,
            'urls': urls,
        }
