import json, os
from name_server import NameServer
from recursive_resolver import RecursiveResolver
from stub_resolver import StubResolver
import dns
import uuid
import time

ROOT_NS_ADDR = ("127.0.0.11", 53053)

def load_server_table(file_name):
    def load_from_json(file_name):
        with open(file_name, "r") as file:
            server_table = json.load(file)
            return server_table

    #iterates through table so that:
    #   every server has childs
    #   these childs doesent have any childs (depth max 1)
    #   but these children occur in new dict entries
    def json_obj_to_server_table_dict(server_table, ns, result):
        #anchor
        if server_table['CHILD'] == 'None':
            result[(ns,server_table['IP'])] = {None:{}}
        else:
            childs_dict = {}
            for child_name, child in server_table['CHILD'].items():
                childs_dict[child_name] = child['IP']
                #rekursive
                json_obj_to_server_table_dict(child, child_name, result)
            result[(ns,server_table['IP'])] = childs_dict

    def server_table_to_servers(dict_server_table):
        server_table = []
        for server_name_server_ip, childs_dict in dict_server_table.items():
            ns, server_ip = server_name_server_ip
            server_table.append(NameServer(ns ,server_ip, childs_dict))
        return server_table

    #code to run
    json_server_table = load_from_json(file_name)
    dict_server_table = {}
    json_obj_to_server_table_dict(json_server_table, 'root', dict_server_table)
    return server_table_to_servers(dict_server_table)

def start_nameservers_and_resolver(servers: NameServer):
    #Start servers
    try:
        for server in servers:
            server.start()
            #print(f'SERVER:{server.name_server_name}:{server.server_ip}:{server.childs_dict} STARTED')
        print('ALL SERVERS STARTED')
    except Exception: 
            print(f'Error could not start server:{server.server_ip}')
    
    #Start resolver
    try:
        resolver = RecursiveResolver()
        resolver.start()
        print(f'RESOLVER: STARTED')
    except Exception:
        print(f'Error could not start resolver:{resolver.resolver_ip}')

def start_stub_and_send_test_request():
    stub_resolver = StubResolver()

    #Milestone 1
    dns_req = 'fuberlin'
    request = dns.creat_dns_request(
        dns_qry_name=dns_req,
        dns_qry_type=1,
        dns_flags_recdesired=1,
        dns_id =str(uuid.uuid4()),
    )
    print('\nTest 0 Milestone 1 stub_resolver')
    print(' This dns request is send from the stub_resolver directly to the name_server(root)')
    print(f' stub_resolver asks for:{dns_req}')
    start = time.time()
    result = stub_resolver.send_request_ip(request, ROOT_NS_ADDR)
    end = time.time()
    print(f' stub_resolver interprets resp as:{result}')
    print(f' Elapsed time:{end - start}')


    #Test 1 Successful
    dns_req = 'easy.homework.fuberlin'
    request = dns.creat_dns_request(
        dns_qry_name=dns_req,
        dns_qry_type=1,
        dns_flags_recdesired=1,
        dns_id =str(uuid.uuid4()),
    )
    print('\nTEST 1 Milestone 2 rekursive_resolver')
    print(' This dns request and the following are requested by the stub_resolver and solved with the rekursive_resolver')
    print(' This dns request should be successful and take around ~ 0.3sec as the rerkusive_resolver has to send 3 requests')
    print(f' stub_resolver asks for:{dns_req}')
    start = time.time()
    result = stub_resolver.send_request_ip(request)
    end = time.time()
    print(f' stub_resolver interprets resp as:{result}')
    print(f' Elapsed time:{end - start}')

    #Test 2 Successful
    dns_req = 'telematik'
    request = dns.creat_dns_request(
        dns_qry_name=dns_req,
        dns_qry_type=1,
        dns_flags_recdesired=1,
        dns_id =str(uuid.uuid4()),
    )
    print('\nTEST 2')
    print(' This dns request should be successful and take around ~ 0.1sec as the rerkusive_resolver has to send 1 requests')
    print(f' stub_resolver asks for:{dns_req}')
    start = time.time()
    result = stub_resolver.send_request_ip(request)
    end = time.time()
    print(f' stub_resolver interprets resp as:{result}')
    print(f' Elapsed time:{end - start}')

    #Test 3 Successful
    dns_req = 'shop.router.telematik'
    request = dns.creat_dns_request(
        dns_qry_name=dns_req,
        dns_qry_type=1,
        dns_flags_recdesired=1,
        dns_id =str(uuid.uuid4()),
    )
    print('\nTEST 3 Milestone 3 cache')
    print(' This dns request should be successful and take around ~ 0.2sec as the rerkusive_resolver has to send 3 requests, but one was already cached')
    print(f' stub_resolver asks for:{dns_req}')
    start = time.time()
    result = stub_resolver.send_request_ip(request)
    end = time.time()
    print(f' stub_resolver interprets resp as:{result}')
    print(f' Elapsed time:{end - start}')

    #Test 4 caching
    print('\nTEST 4 Milestone 3 cache')
    print(' This dns request should be successful and take around ~ 0.0sec as the hole request was already cached')
    print(f' stub_resolver asks for:{dns_req}')
    start = time.time()
    result = stub_resolver.send_request_ip(request)
    end = time.time()
    print(f' stub_resolver interprets resp as:{result}')
    print(f' Elapsed time:{end - start}')


    #Test 5 Function not implemented
    dns_req = 'easy.homework.fuberlin'
    dns_qry_type = 3
    request = dns.creat_dns_request(
        dns_qry_name=dns_req,
        dns_qry_type=dns_qry_type,
        dns_flags_recdesired=1,
        dns_id =str(uuid.uuid4()),
    )
    print('\nTEST 5')
    print(f' This dns request should fail because stub_resolver requests a not supported function')
    print(f' stub_resolver asks for:{dns_req} with dns_qry_type={dns_qry_type}')
    start = time.time()
    result = stub_resolver.send_request_ip(request)
    end = time.time()
    print(f' stub_resolver interprets resp as:{result}')
    print(f' Elapsed time:{end - start}')


    #Test 6 Domain not found
    dns_req = 'thisdomain.does.not.exist.fuberlin'
    request = dns.creat_dns_request(
        dns_qry_name=dns_req,
        dns_qry_type=1,
        dns_flags_recdesired=1,
        dns_id =str(uuid.uuid4()),
    )
    print('\nTEST 6')
    print(f' This dns request should fail because the nameserver does not find this domain')
    print(f' stub_resolver asks for:{dns_req}')
    start = time.time()
    result = stub_resolver.send_request_ip(request)
    end = time.time()
    print(f' stub_resolver interprets resp as:{result}')
    print(f' Elapsed time:{end - start}')

    #Test 7 Successful
    dns_req = 'shop.router.telematik'
    request = dns.creat_dns_request(
        dns_qry_name=dns_req,
        dns_qry_type=1,
        dns_flags_recdesired=1,
        dns_id =str(uuid.uuid4()),
    )
    print('\nTEST 7')
    print(' Sleep 4 seconds')
    time.sleep(4)
    print(' This dns request should be successful and take around ~ 0.3sec as the resolver has to send 3 requests and the previous accessed cache was removed (ttl)')
    print(f' stub_resolver asks for:{dns_req}')
    start = time.time()
    result = stub_resolver.send_request_ip(request)
    end = time.time()
    print(f' stub_resolver interprets resp as:{result}')
    print(f' Elapsed time:{end - start}')

    print('\nDone. Press Crtl+c to exit')

def wait_until_keyerror():
    #Sleep
    try:
        while True: pass
    
    #Stop servers & resolver
    except KeyboardInterrupt:
        os._exit(0)

def main():
    servers = load_server_table('server_table.json')
    start_nameservers_and_resolver(servers)
    start_stub_and_send_test_request()
    wait_until_keyerror()

if __name__ == "__main__":
    main()