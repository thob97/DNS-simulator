import socket
import threading
import logging
import json
from classes import Socket
import loghandler

IP = "0.0.0.0"
PORT = 1234
sys_log = loghandler.sys_log

def process_dns(client: Socket):
        #while client_socket is alive
        while not client.socket._closed:
            ip = client.recv_json()

            #TODO process DNS
            #EXAMPLE
            with open("example.json", "r") as file:
                example_json_answer = json.load(file)

            sys_log.info(f'CLIENT:{client.adress}:IpREQUEST:{ip}:SEND{example_json_answer}')
            
            client.send_json(example_json_answer)

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
    main()
