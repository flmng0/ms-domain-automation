import util

import requests
import json
import os

class Firepower():
    def __init__(self, host, auth):
        self.host = host
        self.request_pre = f"https://{host}/api"

        # Get authentication key from FMC
        headers = {'Content-Type': 'application/json'}
        request_url = f"{self.request_pre}/fmc_platform/v1/auth/generatetoken"

        try:
            req = requests.post(request_url, auth=auth, headers=headers, verify=False)
        except Exception as err:
            print("===== Failed to retrieve authentication code for FMC =====")
            raise

        if 200 <= req.status_code <= 300:
            self.auth_token = req.headers.get('X-auth-access-token', default=None)
            self.domain = req.headers.get('DOMAIN_UUID', default=None)
        else:
            print("===== Failed to retrieve authentication code for FMC =====")
            raise Exception(f"Failed HTTP request. Status: {req.status_code}: {req.reason}")

    def send_request(self, method, endpoint, data=None):
        headers = {'Content-Type': 'application/json', 'X-auth-access-token': self.auth_token}
        request_url = f'{self.request_pre}/fmc_config/v1/domain/{self.domain}/{endpoint}'

        req = requests.request(
                method.upper(), 
                request_url, 
                headers=headers, 
                json=data, 
                verify=False
            )

        if not 200 <= req.status_code <= 300:
            raise Exception(f'Unable to send request: Status {req.status_code}. {req.reason}')

        return req.json()

    def update(self, endpoints, version):
        if os.path.isfile(util.UUIDS_FILE):
            with open(util.UUIDS_FILE, "r") as f:
                uuids = json.load(f)
        else:
            uuids = {}
        
        uuids_dirty = False

        for sa in endpoints:
            if sa in uuids:
                uuid = uuids[sa]

                ips_obj = self.get_object('networkgroups', uuid['ips'])
                urls_obj = self.get_object('urlgroups', uuid['urls'])

            else:
                fmt_string = f'O365_{version}_%s_{sa}'

                obj_json = {
                    'type': 'NetworkGroup',
                    'overridable': True,
                }

                # IPs object
                obj_json['name'] = fmt_string % 'IPs'
                ips_obj = self.create_object('networkgroups', obj_json)

                # URLs object
                obj_json['name'] = fmt_string % 'URLs'
                urls_obj = self.create_object('urlgroups', obj_json)

                uuid = {
                    'ips': ips_obj['id'],
                    'urls': urls_obj['id']
                }

                uuids[sa] = uuid
                uuids_dirty = True

            ips_obj['literals'] = [{'type': 'Network', 'value': ip} for ip in endpoints[sa]['ips']]
            urls_obj['literals'] = [{'type': 'Url', 'url': url} for url in endpoints[sa]['urls']]

            self.update_object('networkgroups', uuid['ips'], ips_obj)
            self.update_object('urlgroups', uuid['urls'], urls_obj)

        if uuids_dirty:
            with open(util.UUIDS_FILE, "w") as f:
                json.dump(uuids, f)

    
    def create_object(self, endpoint, data):
        return self.send_request('POST', f'object/{endpoint}', data)

    def get_object(self, endpoint, obj_id):
        return self.send_request('GET', f'object/{endpoint}/{obj_id}')

    def update_object(self, endpoint, obj_id, data):
        return self.send_request('PUT', f'object/{endpoint}/{obj_id}', data) 

    def delete_object(self, obj):
        return self.send_request('DELETE', f'object/{endpoint}/{obj_id}')

