from util import Util
from firepower import Firepower
from uuid import uuid3, NAMESPACE_URL

import logging
import requests
import signal
import pprint
import getpass
import os
import time

def graceful_exit(sig, frame):
    logging.info('Shutting down, Ctrl-C pressed')
    exit()

def env_or_prompt(name, prompt):
    out = os.getenv(name)
    if out:
        logging.info(f'Using {name} value: {out}')
    else:
        out = input(prompt)

    return out

def run(util, fmc):
    cached_version = util.get_cached_version()
    latest_version = util.get_latest_version()

    if int(cached_version) < int(latest_version):
        logging.info(f'''\
Endpoint update has occured since last run.
    From: {cached_version.strip()}
      To: {latest_version} \
''')
        util.cache_version(latest_version)

        endpoints = util.collect_endpoints()
        
        # TODO: Remove when ready for real use
        print('\nEarly return for testing purposes')
        return

        logging.info('Pushing endpoint updates to Firepower...')
        fmc.update(endpoints, latest_version)

    else:
        logging.info('No update since last run...')

if __name__ == '__main__':
    signal.signal(signal.SIGINT, graceful_exit)

    logging_format = ':: %(levelname)s [%(asctime)s]: %(message)s'
    logging_datefmt = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(level=logging.INFO, format=logging_format, datefmt=logging_datefmt)

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

    try:
        if response in confirm: # Run every N seconds, where N is MSDA_SERVICE_INTERVAL
            delay = env_or_prompt('MSDA_SERVICE_INTERVAL', 'How long to wait between checks, in seconds? [3600] ')
            if delay == '': delay = 3600
            delay = int(delay)

            logging.info(f'Starting updater as a service, running every {delay} seconds...')
            while True:
                run(util, fmc)
                time.sleep(delay)

        elif response in deny: # Run once
            logging.info('Running once...')
            run(util, fmc)

    except Exception as err:
        logging.error(str(err))

