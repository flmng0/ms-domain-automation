from util import Util
from firepower import Firepower
from uuid import uuid3, NAMESPACE_URL

import getpass
import pprint
import os

def env_or_prompt(name, prompt):
    out = os.getenv(name) or input(prompt)

if __name__ == '__main__':
    uuid = uuid3(NAMESPACE_URL, 'network.nt.gov.au')
    util = Util(uuid)

    update_info = util.has_updates()

    fmc_host = env_or_prompt('FMC_HOST', 'Input FMC Host IP: ')
    fmc_user = env_or_prompt('FMC_USER', 'Input FMC Username: ')
    fmc_pass = getpass.getpass('Enter FMC password: ')

    if update_info['did_update']:
        endpoints = util.collect_endpoints()

        fmc = Firepower(fmc_host, (fmc_user, fmc_pass))
        fmc.update(endpoints)


# Some pseudo-code for workflow:
'''

id = uuid.uuidN(uuid.NAMEPSACE_URL, "network.nt.gov.au")
util = Util(id)

update_info = util.has_updates()

if update_info['did_update']:
    endpoints = util.collect_endpoints()
    
    # Firepower class will be defined in a separate module
    fmc = Firepower(host, auth)
    fmc.update(endpoints)

    # SMTP class will be defined in a separate module
    changes = util.collect_changes()
    smtp = SMTP(host, auth)
    smtp.report(changes)


#### Util.collect_endpoints():
    endpoints = {}

    json = requests.... # Steal from get_service_areas()

    for obj in json:
        if not obj['serviceArea'] in endpoints:
            obj['serviceArea'] = {}

        obj['serviceArea'] += {ip for ip in obj['ips']}

'''

