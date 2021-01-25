import requests

class Firepower():
    def __init__(self, host, auth):
        self.host = host
        self.request_pre = f"https://{host}/api"

        # TODO: Handle SSL verification for POST requests
        requests.packages.urllib3.disable_warnings()

        # Get authentication key from FMC
        headers = {'Content-Type': 'application/json'}
        request_url = f"{self.request_pre}/fmc_platform/v1/auth/generatetoken"

        req = requests.post(request_url, auth=auth, headers=headers, verify=False)

        self.auth_token = req.headers.get('X-auth-access-token', default=None)
        self.domain = req.headers.get('DOMAIN_UUID', default=None)

        if not self.auth_token:
            # TODO: Handle auth error here
            pass
    
    def send_request(self, method, endpoint, data=None):
        headers = {'Content-Type': 'application/sjon', 'X-auth-access-token': self.auth_token}
        request_url = f'{self.request_pre}/fmc_config/v1/domain/{self.domain}/{endpoint}'

        request_func = {
            'POST': requests.post,
            'PUT': requests.put,
            'DELETE': requests.delete,
            'GET': requests.get,
        }[method.upper()]

        # TODO: SSL Verification
        req = request_func(request_url, headers=headers, json=data, verify=None)

        return req.json()

    def update(self, endpoints):
        pass
    
    def create_object(self, endpoint, data):
        call_url = f'object/{endpoint}'

        uuid = self.send_request('POST', call_url, data)
        
        return Object(self, uuid, endpoint)

    def get_object(self, endpoint, uuid):
        call_url = f'object/{endpoint}/{uuid}'
        return self.send_request('GET', call_url)


class Object():
    def __init__(self, fmc, uuid, endpoint):
        self.fmc = fmc
        self.uuid = uuid
        self.endpoint = endpoint

    def uuid(self):
        return self.uuid

    def delete(self):
        call_url = f'object/{self.endpoint}/{self.uuid}'
        return self.fmc.send_request('DELETE', call_url)

    def update(self, data):
        call_url = f'object/{self.endpoint}/{self.uuid}'
        return self.fmc.send_request('PUT', call_url, data)
