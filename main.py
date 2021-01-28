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

def main():
    requests.packages.urllib3.disable_warnings()

    uuid = uuid3(NAMESPACE_URL, 'network.nt.gov.au')
    util = Util(uuid)

    cached_version = util.get_cached_version()
    latest_version = util.get_latest_version()

    if int(cached_version) < int(latest_version):
        print(f'Endpoint update has occured since last run.')
        print(f'    From: {cached_version}')
        print(f'      To: {latest_version}')
        endpoints = util.collect_endpoints()
        print(endpoints.keys())
        return

        fmc_host = env_or_prompt('FMC_HOST', 'Input FMC Host IP: ')
        fmc_user = env_or_prompt('FMC_USER', 'Input FMC Username: ')
        fmc_pass = getpass.getpass('Enter FMC password: ')

        fmc = Firepower(fmc_host, (fmc_user, fmc_pass))
        fmc.update(endpoints, latest_version)

if __name__ == '__main__':
    main()
