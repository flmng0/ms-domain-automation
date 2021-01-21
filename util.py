import requests
import os

# Constants
APP_SLUG = 'msda'
CACHE_PATH = f'/var/lib/{APP_SLUG}'
VERISON_FILE f'{CACHE_PATH}/version'

# O365 Constants
URL_PREFIX = 'https://endpoints.office.com'

def has_updates(client_id, instance='Worldwide', proxies=None):
    # Construct the request URL
    request_url = f'{URL_PREFIX}/version?clientrequestid={client_id}'

    # Send the actual request
    data = requests.get(request_url, proxies=proxies).json()

    for obj in data:
        if obj['instance'] == instance:
            latest_version = int(obj['latest'])

    base = os.path.dirname(VERSION_FILE)
    if not os.path.exists(base):
        os.makedirs(base)

    old_version = 0
    if os.path.isfile(VERSION_FILE):
        with open(VERSION_FILE, 'r') as f:
            old_version = int(f.readline())
    
    updated = old_version < latest_version

    if updated:
        with open(VERSION_FILE, 'w') as f:
            f.write(str(latest_version))

    return {
        'did_update': updated,
        'old_version': old_version,
    }

def get_service_areas(client_id, instance='Worldwide', proxies=None):
    request_url = f'{URL_PREFIX}/endpoints/{instance}/?clientrequestid={client_id}'

    data = requests.get(request_url, proxies=proxies).json()

    return {obj['id']: obj['serviceArea'] for obj in data}


