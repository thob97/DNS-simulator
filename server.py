import socket
import threading
import logging
import json
from classes import Socket
import loghandler
import threading

DATASIZE = 512
#TODO del of json
PORT = 53053

#TODO
sys_log = loghandler.sys_log

class Server:
    def __init__(self,server_ip,childs_dict):
        self.server_ip = server_ip
        self.childs_dict = childs_dict
        self.server_socket = None
        self.client_socket = None
        self.client_adress = None

    def send_json(self, json_obj):
        self.client_socket.send(json.dumps(json_obj).encode('utf-8'))

    def recv_json(self):
        json_str = self.client_socket.recv(DATASIZE).decode('utf-8')
        return json.loads(json_str)

    def start_server(self):
        #create socket(IP4, tcp)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.server_ip, PORT))
        #listen for connections
        self.server_socket.listen()

        while True:
            #new connecting client
            self.client_socket, self.client_adress = self.server_socket.accept()

            threading.Thread(target=self.listen_for_queries, args=()).start()

    def listen_for_queries(self):
            #while client_socket is alive
            while not self.client_socket._closed:
                

                #TODO process DNS
                #EXAMPLE
                #with open("example.json", "r") as file:
                #    example_json_answer = json.load(file)

                #sys_log.info(f'CLIENT:{client.adress}:IpREQUEST:{ip}:SEND{example_json_answer}')
                
                #client.send_json(example_json_answer)
                request = self.client_socket.recv(512).decode('utf-8')
                self.client_socket.send((self.childs_dict[request]['IP']).encode('utf-8'))

def load_server_table():
    with open("server_table.json", "r") as file:
        server_table = json.load(file)
        return server_table

#iterates through table so that:
#   every server has childs
#   the child doesent have any childs
def interpret_server_table(server_table, result):
    if server_table['CHILD'] == 'None':
        result += [(Server(server_table['IP'], None))]
    else:
        childs_dict = {}
        for child_name, child in server_table['CHILD'].items():
            childs_dict[child_name] = {'IP':child['IP']}
            
            #rekursive
            interpret_server_table(child, result)
        result += [(Server(server_table['IP'], childs_dict))]
        



def start_servers(servers: Server):
    for server in servers:
        print(server.server_ip, server.childs_dict)
        threading.Thread(target=server.start_server).start()
        

        #TODO catch errors


def main():

    
    #create socket(IP4, tcp)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP,PORT))
    #listen for connections
    server_socket.listen()

    while True:
        #new connecting client
        client_socket, client_adress = server_socket.accept()
        client = Socket(socket=client_socket, adress=client_adress)

        sys_log.info(f'CLIENT:{client_adress}:connected')

        threading.Thread(target=process_dns, args=(client,)).start()


if __name__ == "__main__":
    #main()
    data = load_server_table()

    servers = []
    interpret_server_table(data, servers)

    start_servers(servers)
