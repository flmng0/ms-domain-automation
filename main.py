from util import Util
from firepower import Firepower
from uuid import uuid3, NAMESPACE_URL

import requests
import pprint
import getpass
import os
import time

def env_or_prompt(name, prompt):
    out = os.getenv(name)
    if out:
        print(f'Using {name} value: {out}')
    else:
        out = input(prompt)

    return out

def main(util, fmc):
    cached_version = util.get_cached_version()
    latest_version = util.get_latest_version()

    if int(cached_version) < int(latest_version):
        print(f'Endpoint update has occured since last run.')
        print(f'    From: {cached_version}')
        print(f'      To: {latest_version}')
        endpoints = util.collect_endpoints()
        print(endpoints.keys())
        return

        fmc.update(endpoints, latest_version)

if __name__ == '__main__':
    # Setup common interfaces
    requests.packages.urllib3.disable_warnings()

    # Initialise utility class
    uuid = uuid3(NAMESPACE_URL, 'network.nt.gov.au')
    util = Util(uuid)

    # Get FMC login
    fmc_host = env_or_prompt('FMC_HOST', 'Input FMC Host IP: ')
    fmc_user = env_or_prompt('FMC_USER', 'Input FMC Username: ')
    fmc_pass = getpass.getpass('Enter FMC password: ')

    # fmc = Firepower(fmc_host, (fmc_user, fmc_pass))
    fmc = "rando test str"

    # TODO: Initialize SMTP connection

    # Check if the user wants the script ran continually
    confirm = { 'yes', 'ye', 'y' }
    deny = { 'no', 'n', '' }

    response = None
    while True:
        response = input('Should the script be run as a service? [y/N] ').lower()
        if response in confirm | deny:
            break

    if response in confirm: # Run every N seconds, where N is MSDA_SERVICE_INTERVAL
        delay = env_or_prompt('MSDA_SERVICE_INTERVAL', 'How long to wait between checks, in seconds? [3600] ')
        if delay == '': delay = 3600
        delay = int(delay)

        while True:
            main(util, fmc)
            time.sleep(delay)

    elif response in deny: # Run once
        main(util, fmc)

