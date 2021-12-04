import socket
import os
import dns
import uuid
import loghandler

RESOLVER_IP = "127.0.0.10"
PORT = 53053
DATASIZE = 512

class StubResolver():
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.logger = loghandler.new_log('stub')

    def hanlde_dns_msg(self, dns_msg):
        #only accept dns respons (we are no server)
        if dns_msg['dns_flags_response'] == 1:
            #sucsess
            if dns_msg['dns_flags_rcode'] == 0:
                return dns_msg['dns_a']

            elif dns_msg['dns_flags_rcode'] == 2:
                return 'Server Failure'

            elif dns_msg['dns_flags_rcode'] == 3:
                return 'Non-Existent Domain'

            #request not implemented (dns.qry.type)
            elif dns_msg['dns_flags_rcode'] == 4:
                return 'Not Implemented'

            else:
                return 'Some other error flag'

    def send_request_ip(self, dns_request, server_adr=(RESOLVER_IP,PORT)):
        try:
            dns.send_dns_msg(self.socket, server_adr, dns_request)
            self.logger.info(f'<IP address>:{server_adr}|<req send>:{dns_request}')

            dns_msg, resolver_adr = dns.recv_dns_msg(self.socket)
            self.logger.info(f'<IP address>:{resolver_adr}|<resp recv>:{dns_msg}')

            response = self.hanlde_dns_msg(dns_msg)
            return response

        except KeyboardInterrupt:
            print(f'CLIENT TERMINATED')
            os._exit(0)
            




def main():
    stub_resolver = StubResolver()
    dns_request = dns.creat_dns_request(
        dns_qry_name='easy.homework.fuberlin',
        dns_qry_type=1,
        dns_flags_recdesired=1,
        dns_id =str(uuid.uuid4()),
    )
    result = stub_resolver.send_request_ip(dns_request)
    print(f'CLIENT RECV RESULT:{result}')

if __name__ == "__main__":
    main()
