import socket
import threading
from cache import DNSCache
import loghandler
import dns

IP = "127.0.0.10"
PORT = 53053
DATASIZE = 512
ROOT_NS_ADDR = ("127.0.0.11", 53053)

class RecursiveResolver(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.socket = None
        self.resolver_ip = IP
        #remember the adr from each client request
        self.client_list = {}
        self.dnscache = DNSCache(50)
        self.logger = loghandler.new_log(self.resolver_ip)

    #thread methods
    def run(self):
        self.start_resolver()

    def del_client_adr(self, dns_msg):
        client_adr = self.client_list[dns_msg['dns_id']]
        del self.client_list[dns_msg['dns_id']]
        return client_adr
    def save_client_adr(self, dns_msg, client_adr):
        self.client_list[dns_msg['dns_id']] = client_adr


    def start_resolver(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.resolver_ip, PORT))
        #start for each client a thread
        while True:
            dns_request, client_adr = dns.recv_dns_msg(self.socket)
            threading.Thread(target=self.process_dns, args=(dns_request, client_adr)).start()

    def process_dns(self, dns_msg, client_adr):
        #if request
        if dns_msg['dns_flags_response'] == 0:
            self.logger.info(f'<IP address>:{client_adr}|<req rcv>:{dns_msg}')

            #if request in cache
            dns_msg_entry = self.dnscache.get_longest_prefix(dns_msg)
            if dns_msg_entry is not None:
                #if cached entry is authorative
                if dns_msg_entry['dns_resp_name'] == dns_msg['dns_qry_name']:
                    dns_msg_entry['dns_id'] = dns_msg['dns_id']
                    dns_msg = dns_msg_entry
                else:
                    self.save_client_adr(dns_msg, client_adr)
                    #dna_a is missing port
                    client_adr = (dns_msg_entry['dns_a'], PORT)
                    dns_msg = dns.creat_dns_request(
                        dns_qry_name=dns_msg['dns_qry_name'],
                        dns_qry_type=dns_msg['dns_qry_type'],
                        dns_flags_recdesired=dns_msg['dns_flags_recdesired'],
                        dns_id=dns_msg['dns_id'],
                    )
        
            #if not cached
            else:
                self.save_client_adr(dns_msg, client_adr)
                client_adr = ROOT_NS_ADDR
           
        #if response
        else:
            self.logger.info(f'<IP address>:{client_adr}|<resp rcv>:{dns_msg}')

            #if any Server Failure
            if dns_msg['dns_flags_rcode'] != 0:
                client_adr = self.del_client_adr(dns_msg)

            else:
                self.dnscache.add(dns_msg)

                #if we have reached the requested NS
                if dns_msg['dns_flags_authoritative'] == 1:
                    client_adr = self.del_client_adr(dns_msg)

                #if ongoing response
                else:
                    #dna_a is missing port
                    client_adr = (dns_msg['dns_a'], PORT)
                    dns_msg = dns.creat_dns_request(
                        dns_qry_name=dns_msg['dns_qry_name'],
                        dns_qry_type=dns_msg['dns_qry_type'],
                        dns_flags_recdesired=dns_msg['dns_flags_recdesired'],
                        dns_id=dns_msg['dns_id'],
                    )

        #send dns msg to client or NS
        dns.send_dns_msg(self.socket, client_adr, dns_msg)
        self.logger.info(f'<IP address>:{client_adr}|<req snd>:{dns_msg}')



def main():
    resolver = RecursiveResolver()
    resolver.start()

if __name__ == "__main__":
    main()