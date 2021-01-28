import requests
import os

# Constants
CACHE_PATH = f"/home/admtimda/ms-domain-automation/cache"
UUIDS_FILE = f"{CACHE_PATH}/uuids.json"
VERSION_FILE = f"{CACHE_PATH}/version"
VERSION_LENGTH = 10

# O365 Constants
O365_PREFIX = "https://endpoints.office.com"

class Util():
    def __init__(self, client_id, instance="Worldwide", proxies=None):
        self.client_id = client_id
        self.instance = instance
        self.proxies = proxies

    # Get the latest version of the O365 endpoints.
    def get_latest_version(self):
        # Construct the request URL
        request_url = f"{O365_PREFIX}/version?clientrequestid={self.client_id}"

        # Send the actual request
        data = requests.get(request_url, proxies=self.proxies).json()

        # Find the version for the requested instance
        obj = next(obj for obj in data if obj["instance"] == self.instance)
        return obj["latest"]

    # Get the version that the endpoints were at the last time this
    # script was run.
    def get_cached_version(self):
        version = '0' * VERSION_LENGTH
        if os.path.isfile(VERSION_FILE):
            with open(VERSION_FILE, "r") as f:
                version = f.readline()

        return version

    def cache_version(self, version):
        # Create the directory for the version file if it doesn't already
        # exist
        base_dir = os.path.dirname(VERSION_FILE)
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        with open(VERSION_FILE, "w") as f:
            f.write(version)


    # Collect all endpoints as a dictionary:
    #   endpoints {
    #       '<serviceArea1>': { 'ips': set with ips, ' urls': set with urls },
    #       '<serviceArea1>': { 'ips': set with ips, ' urls': set with urls },
    #       ...
    #       '<serviceAreaN>': { 'ips': set with ips, ' urls': set with urls },
    #   }
    def collect_endpoints(self):
        out = {}

        request_url = f"{O365_PREFIX}/endpoints/{self.instance}/?clientrequestid={self.client_id}&NoIPv6=true"
        data = requests.get(request_url, proxies=self.proxies).json()

        for obj in data:
            sa = obj['serviceArea']
            
            # Initialize the sets if they don't exist
            #
            # Sets are used instead of lists, because it forces unique
            # items (no repeats).
            if not sa in out:
                out[sa] = {
                    'ips': set(),
                    'urls': set(),
                }

            # If there are IPs listed in this endpoint, add them to the
            # `ips` set.
            if 'ips' in obj: 
                out[sa]['ips'] = out[sa]['ips'] | {ip for ip in obj['ips']}

            # If there are URLs listed in this endpoint, add them to the
            # `urls` set.
            if 'urls' in obj: 
                # FMC processes URLs by substring matching and doesn't
                # support traditional wildcard matching (*).
                out[sa]['urls'] = out[sa]['urls'] | {url.replace('*','') for url in obj['urls']}
            
        return out
