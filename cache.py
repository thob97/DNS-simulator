import threading
import time

class DNSCache(threading.Thread):
    def __init__(self, length):
        threading.Thread.__init__(self)
        self.length = length
        self.cache = {}
        self.start()

    #thread methods
    def run(self):
        self.start_cache()
    
    #remove cache entry if time_past > ttl
    def start_cache(self):
        while True:
            try:
                for dns_resp_name, info in self.cache.items():
                    dns_resp_ttl = info['dns_resp_ttl']
                    time_stamp = info['time_stamp']
                    time_past = time.time() - time_stamp
                    if time_past > dns_resp_ttl:
                        del self.cache[dns_resp_name]
                time.sleep(1)
            #dictionary changed size during iteration
            except RuntimeError:
                pass

    def add(self, dns_msg):
        if self.length >= len(self.cache):
            self.cache[(dns_msg['dns_resp_name'], dns_msg['dns_qry_type'])] = {
                'dns_msg':dns_msg,
                'dns_resp_ttl':dns_msg['dns_resp_ttl'], 
                'time_stamp':time.time()
                }
    
    def get_longest_prefix(self, dns_msg):
        dns_req = dns_msg['dns_qry_name']
        #get dns_qry_name in prefered sruct: 192.168.0.1 -> 1, 0.1, 168.0.1, 192.168.0.1
        dns_req = dns_req.split('.')
        dns_req.reverse()
        for i, _ in enumerate(dns_req[1:]):
            dns_req[i+1] = dns_req[i+1] + '.' + dns_req[i]
        #1, 0.1, 168.0.1, 192.168.0.1 -> 192.168.0.1, 168.0.1, 0.1, 1
        dns_req.reverse()
        for prefix in dns_req:
            try:
                entry = self.cache[(prefix, dns_msg['dns_qry_type'])]
                return entry['dns_msg']
            except KeyError:
                pass
        return None