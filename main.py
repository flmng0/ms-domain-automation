from util import Util
from firepower import Firepower
from uuid import uuid3, NAMESPACE_URL

import requests
import pprint
import getpass
import os

def env_or_prompt(name, prompt):
    out = os.getenv(name)
    if out:
        print(f'Using {name} value: {out}')
    else:
        out = input(prompt)

    return out

if __name__ == '__main__':
    requests.packages.urllib3.disable_warnings()

    fmc_host = env_or_prompt('FMC_HOST', 'Input FMC Host IP: ')
    fmc_user = env_or_prompt('FMC_USER', 'Input FMC Username: ')
    fmc_pass = getpass.getpass('Enter FMC password: ')

    print(fmc_host, fmc_user, fmc_pass)

    uuid = uuid3(NAMESPACE_URL, 'network.nt.gov.au')
    util = Util(uuid)

    update_info = util.has_updates()

    if update_info['did_update']:
        print(f'Endpoint update has occured since last run.')
        print(f'    From: {update_info["old_version"]}')
        print(f'      To: {update_info["new_version"]}')
        endpoints = util.collect_endpoints()
        print(endpoints.keys())

        exit()
        fmc = Firepower(fmc_host, (fmc_user, fmc_pass))
        fmc.update(endpoints, update_info['new_version'])

