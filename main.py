from util import Util, VERSION_FILE
import uuid
import pprint
import os

if __name__ == '__main__':
    id = uuid.uuid3(uuid.NAMESPACE_URL, "network.nt.gov.au")
    util = Util(id)

    pp = pprint.PrettyPrinter(indent=4)

    print('\n\n=========== Updates? ============')
    pp.pprint(util.has_updates())

    print('\n\n=========== Service Areas ============')
    pp.pprint(util.get_service_areas())

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

