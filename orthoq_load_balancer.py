import requests
import json
from secret import URLS

'''
Load Balancer to manage distributing work evenly between servers
'''

class OrthoQLoadBalancer:

    def __init__(self, urls=URLS):
        self.urls = urls

    def try_status_check(self, url):
        ''' check the /status endpoint for a url '''
        try:
            status_req = requests.get(url + "/status")
            status = json.loads(status_req.text)
            qlen = status["queue_len"]
            return qlen
        except requests.exceptions.ConnectionError as e:
            return float('inf')

    def check_statuses(self):
        ''' check all servers and record the least busy one '''
        min_queue_len = float('inf')
        min_queue_name = ""
        for k in self.urls.keys():
            url = self.urls[k]
            qlen = self.try_status_check(url)
            if qlen < min_queue_len:
                min_queue_len = qlen
                min_queue_name = k
        out = {
            "url": self.urls[min_queue_name],
            "name": min_queue_name,
            "queue_len": min_queue_len
        }
        return out

if __name__ == "__main__":
    lb = OrthoQLoadBalancer()
    print(lb.check_statuses())