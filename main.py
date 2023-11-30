import json
from urllib.parse import urlparse

import yaml
import requests
import time


class APIHealthCheck:
    def __init__(self, endpoint_data):
        self.endpoint_data = endpoint_data
        self.domain_stats = {}

    def make_request(self, endpoint):
        method = endpoint.get('method', 'GET')
        url = endpoint.get('url')
        headers = endpoint.get('headers', {})
        body = endpoint.get('body', None)

        response = self.send_request(url, method, headers, body)
        if response:
            latency = response.elapsed.total_seconds() * 1000

            if 200 <= response.status_code < 300 and latency < 500:
                result = 'UP'
            else:
                result = 'DOWN'
            self.update_domain_stats(url, result)

    def send_request(self, url, method, headers, body):
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST' and body:
            response = requests.post(url, headers=headers, json=json.loads(body))
        return response

    def update_domain_stats(self, url, result):
        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        if domain not in self.domain_stats:
            self.domain_stats[domain] = {'total': 0, 'up': 0}

        self.domain_stats[domain]['total'] += 1

        if result == 'UP':
            self.domain_stats[domain]['up'] += 1

    def log_domain_stats(self):
        for domain, stats in self.domain_stats.items():
            availability_percentage = (stats['up'] / stats['total']) * 100 if stats['total'] > 0 else 0
            print(f"{domain} has {availability_percentage:.2f}% availability percentage")


def read_yaml_file(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        sys.exit(1)

    yaml_file_path = sys.argv[1]

    api_call = APIHealthCheck([])

    while True:
        endpoints_data = read_yaml_file(yaml_file_path)
        api_call.endpoint_data = endpoints_data

        for endpoint in endpoints_data:
            api_call.make_request(endpoint)

        api_call.log_domain_stats()
        time.sleep(15)
