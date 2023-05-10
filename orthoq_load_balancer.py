import requests
import json
from secrets import URLS

class OrthoQLoadBalancer:

    def __init__(self, urls=URLS):
        self.urls = urls

    def try_status_check(self, ip):
        try:
            print("===============================")
            print(ip + "/status")
            status_req = requests.get(ip + "/status")
            print(status_req.text)
            print(status_req.status_code)
            print("===============================")
            status = json.loads(status_req.text)
            qlen = status["queue_len"]
            return qlen
        except requests.exceptions.ConnectionError as e:
            return float('inf')

    def check_statuses(self):
        min_queue_len = float('inf')
        min_queue_name = ""
        for k in self.urls.keys():
            ip = self.urls[k]
            qlen = self.try_status_check(ip)
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