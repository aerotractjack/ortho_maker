import requests
import json
from secret_manager import get_urls

'''
Load Balancer to manage distributing work evenly between servers
'''

class OrthoQLoadBalancer:

    def __init__(self):
        pass

    @property
    def urls(self):
        return get_urls()

    def try_status_check(self, url):
        ''' check the /status endpoint for a url '''
        try:
            status_req = requests.get(url + "/status")
            status = json.loads(status_req.text)
            return status
        except requests.exceptions.ConnectionError as e:
            return float('inf')

    def check_statuses(self):
        ''' check all servers and record the least busy one '''
        min_queue_len = float('inf')
        min_queue_name = ""
        for k in self.urls.keys():
            url = self.urls[k]
            qlen = self.try_status_check(url)["queue_len"]
            if qlen < min_queue_len:
                min_queue_len = qlen
                min_queue_name = k
        out = {
            "url": self.urls[min_queue_name],
            "name": min_queue_name,
            "queue_len": min_queue_len
        }
        return out

    def show_all_statuses(self):
        ''' return the statuses for all servers '''
        outs = []
        for k in self.urls.keys():
            url = self.urls[k]
            status = self.try_status_check(url)
            out = {
                "url": url,
                "name": k,
                "queue_len": status["queue_len"],
                "contents": status["contents"],
                "bodies": status["bodies"]
            }
            outs.append(out)
        return outs

if __name__ == "__main__":
    lb = OrthoQLoadBalancer()
    print(lb.check_statuses())
