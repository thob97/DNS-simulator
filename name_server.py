import socket
import threading
import loghandler
import threading
import dns
import time

DATASIZE = 512
PORT = 53053

#TODO log
sys_log = loghandler.sys_log

class NameServer(threading.Thread):
    def __init__(self,name_server_name,server_ip,childs_dict):
        threading.Thread.__init__(self)
        self.name_server_name = name_server_name
        self.server_ip = server_ip
        self.childs_dict = childs_dict
        self.socket = None
        self.ttl = 1
        self.logger = loghandler.new_log(self.server_ip)
        
    #threading methods
    def run(self):
        self.start_server()

    def start_server(self):
        #create socket(IP4, udp)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.server_ip, PORT))

        #for each client open a thread
        while True:
            data, client_adress = dns.recv_dns_msg(self.socket)
            threading.Thread(target=self.process_dns, args=(data, client_adress)).start()

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
                return prefix, self.childs_dict[prefix]
            except KeyError:
                pass
        return None, None

    def process_dns(self, dns_msg, client_adr):
        #only accept request
        if dns_msg['dns_flags_response'] == 0:
            self.logger.info(f'<IP address>:{client_adr}|<req rcv>:{dns_msg}')

            #if unsuported function is requested
            if dns_msg['dns_qry_type'] != 1:
                dns_msg = dns.creat_dns_response(
                    dns_qry_name=dns_msg['dns_qry_name'],
                    dns_qry_type=dns_msg['dns_qry_type'],
                    dns_flags_recdesired=dns_msg['dns_flags_recdesired'],
                    dns_id=dns_msg['dns_id'],
                    dns_flags_recavail=0,
                    #Not Implemented
                    dns_flags_rcode=4,
                    dns_flags_authoritative=0,
                    dns_count_answers=0,
                    dns_ns=self.name_server_name,
                    dns_resp_type=dns_msg['dns_qry_type'],
                    dns_resp_name=None,
                    dns_a=None,
                    dns_resp_ttl=self.ttl
                )

            #if record is requested
            else:
                #dns lookup
                dns_resp_name, dns_a = self.get_longest_prefix(dns_msg)

                #If entry not found on this server (Non-Existent Domain)
                if dns_a is None:
                    dns_msg = dns.creat_dns_response(
                        dns_qry_name=dns_msg['dns_qry_name'],
                        dns_qry_type=dns_msg['dns_qry_type'],
                        dns_flags_recdesired=dns_msg['dns_flags_recdesired'],
                        dns_id=dns_msg['dns_id'],
                        dns_flags_recavail=0,
                        #Non-Existent Domain
                        dns_flags_rcode=3,
                        dns_flags_authoritative=0,
                        dns_count_answers=0,
                        dns_ns=self.name_server_name,
                        dns_resp_type=dns_msg['dns_qry_type'],
                        dns_resp_name=None,
                        dns_a=None,
                        dns_resp_ttl=self.ttl
                    )
                    
                #if found
                else:
                    dns_msg = dns.creat_dns_response(
                        dns_qry_name=dns_msg['dns_qry_name'],
                        dns_qry_type=dns_msg['dns_qry_type'],
                        dns_flags_recdesired=dns_msg['dns_flags_recdesired'],
                        dns_id=dns_msg['dns_id'],
                        dns_flags_recavail=0,
                        #DNS Query completed successfully
                        dns_flags_rcode=0,
                        #if server is authoritative
                        dns_flags_authoritative= 1 if dns_msg['dns_qry_name'] == dns_resp_name else 0,
                        dns_count_answers=1,
                        dns_ns=self.name_server_name,
                        dns_resp_type=dns_msg['dns_qry_type'],
                        dns_resp_name=dns_resp_name,
                        dns_a=dns_a,
                        dns_resp_ttl=self.ttl
                    )

            #simulated delay to show efects of cache
            time.sleep(.1)
            #send dns msg to client or NS
            dns.send_dns_msg(self.socket, client_adr, dns_msg)
            self.logger.info(f'<IP address>:{client_adr}|<resp send>:{dns_msg}')
