import socket
import threading
import json
from classes import Socket

IP = "127.0.0.11"
PORT = 53053
DATASIZE = 1024


def request_ip(server: Socket):
    #while server_socket is alive
    while not server.socket._closed:
        #wait for keyboard input
        ddns = input()

        #TODO request DNS
        #EXAMPLE
        example_json = '{ "ip":"127.0.0.1" }'

        #server.send_json(example_json)
        #json_answer = server.recv_json()
        #print('From server:',json_answer)

        server.socket.send(ddns.encode('utf-8'))
        response = server.socket.recv(512).decode('utf-8')

        print(response)


def main():
    #connect socket(IP4, tcp)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((IP,PORT))
    server = Socket(socket= server_socket, adress= None)

    #start threads
    threading.Thread(target= request_ip, args=(server,)).start()

if __name__ == "__main__":
    main()
