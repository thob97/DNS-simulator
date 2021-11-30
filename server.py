import socket
import threading
import logging
import json
from classes import Socket
import loghandler
import threading

DATASIZE = 512
PORT = 53053

#TODO log
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

    #TODO
    def process_dns():
        pass

    def start_server(self):
        #create socket(IP4, tcp)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.server_ip, PORT))
        #listen for connections
        self.server_socket.listen()

        while True:
            try:
                #new connecting client
                self.client_socket, self.client_adress = self.server_socket.accept()
                threading.Thread(target=self.listen_for_queries, args=()).start()
            
            except Exception: #some weird error
                pass
                #TODO close server socket

    def listen_for_queries(self):
            #while client_socket is alive
            while not self.client_socket._closed:
                try:

                    #TODO process DNS
                    #EXAMPLE
                    #with open("example.json", "r") as file:
                    #    example_json_answer = json.load(file)

                    #sys_log.info(f'CLIENT:{client.adress}:IpREQUEST:{ip}:SEND{example_json_answer}')
                    
                    #client.send_json(example_json_answer)
                    request = self.client_socket.recv(512).decode('utf-8')
                    self.client_socket.send((self.childs_dict[request]['IP']).encode('utf-8'))
                except Exception: #some send / recv error from this function
                    #TODO close client socket
                    pass


def load_server_table(file_name):
    def load_from_json(file_name):
        with open(file_name, "r") as file:
            server_table = json.load(file)
            return server_table

    #iterates through table so that:
    #   every server has childs
    #   these childs doesent have any childs (depth max 1)
    #   but these children occur in new dict entries
    def json_obj_to_server_table_dict(server_table, result):
        if server_table['CHILD'] == 'None':
            result += [(Server(server_table['IP'], None))]
        else:
            childs_dict = {}
            for child_name, child in server_table['CHILD'].items():
                childs_dict[child_name] = {'IP':child['IP']}
                
                #rekursive
                json_obj_to_server_table_dict(child, result)
            result += [(Server(server_table['IP'], childs_dict))]

    #TODO 
    def table_dict_to_servers():
        pass


def start_servers(servers: Server):
    for server in servers:
        try:
            print(server.server_ip, server.childs_dict)
            threading.Thread(target=server.start_server).start()
        except Exception: #KeyboardInterrput
            pass
            #TODO close all threads / join


def main():
    pass

if __name__ == "__main__":
    #main()
    data = load_server_table()

    servers = []
    interpret_server_table(data, servers)

    start_servers(servers)
