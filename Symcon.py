"""This is the Symcon module which can be used to transfer data to IP Symcon"""
import json
import requests
from requests.auth import HTTPBasicAuth

class Symcon():
    """The Symcon class can be used to establish a connection to the IP Symcon system"""
    def __init__(self):
        self.symcon_url = "http://192.168.0.20:83/api/"

    def set_symcon_url(self, symcon_url):
        """Use this to specify the Symcon Url to the API, for example http://host:port/api/"""
        self.symcon_url = symcon_url

    def invoke_ips_rpc(self, method, parameters):
        """Calls the remote procedure of the target Symcon server"""
        headers = {'content-type': 'application/json'}
        auth = HTTPBasicAuth("michael.jata@googlemail.com", "geenial2k7Jata")

        payload = {
            'method': method,
            'params': parameters,
            'jsonrpc': '2.0',
            'id': '0'
            }

        response = requests.post(self.symcon_url, auth=auth, headers=headers, data=json.dumps(payload))
        return response
