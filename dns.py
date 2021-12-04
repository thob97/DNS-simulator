import json

DATASIZE = 512

def send_dns_msg(socket, client_adr, dns_msg):
    #dumps: json -> str (json acts like a dict)
    data = json.dumps(dns_msg).encode('utf-8')
    socket.sendto(data, client_adr)

def recv_dns_msg(socket):
    data, client_ipv4 = socket.recvfrom(DATASIZE)
    #loads: str -> json (json acts like a dict)
    dns_msg = json.loads(data.decode('utf-8'))
    return dns_msg, client_ipv4
        
def creat_dns_request(dns_qry_name, dns_qry_type, dns_flags_recdesired, dns_id):
    dns_req = {}

    #0:is query 1:is response
    dns_req['dns_flags_response'] = 0
    #requested query name
    dns_req['dns_qry_name'] = dns_qry_name
    #1 for a record
    dns_req['dns_qry_type'] = dns_qry_type
    #recursive desired
    dns_req['dns_flags_recdesired'] = dns_flags_recdesired

    #Transaction ID
    dns_req['dns_id'] = dns_id

    return dns_req

def creat_dns_response(dns_qry_name, dns_qry_type, dns_flags_recdesired, dns_id, dns_flags_recavail, dns_flags_rcode, dns_flags_authoritative, dns_count_answers, dns_ns, dns_resp_type, dns_resp_name, dns_a, dns_resp_ttl):
    dns_res = {}

    #0:is query 1:is response
    dns_res['dns_flags_response'] = 1
    #requested query name
    dns_res['dns_qry_name'] = dns_qry_name
    #1 for a record (everything else dns_flags_rcode=4)
    dns_res['dns_qry_type'] = dns_qry_type
    #recursive desired
    dns_res['dns_flags_recdesired'] = dns_flags_recdesired

    #Transaction ID
    dns_res['dns_id'] = dns_id

    #recursion not available
    dns_res['dns_flags_recavail'] = dns_flags_recavail
    #reply code 0:DNS Query completed successfully 2:Server Failure 3:Non-Existent Domain 4:Not Implemented
    dns_res['dns_flags_rcode'] = dns_flags_rcode
    #is nameserver authoritative of query name (lookup finished)
    dns_res['dns_flags_authoritative'] = dns_flags_authoritative
    #count of nameserver answers received (multiple answers)
    dns_res['dns_count_answers'] = dns_count_answers

    #NS which send this respond
    dns_res['dns_ns'] = dns_ns
    #1 for a record
    dns_res['dns_resp_type'] = dns_resp_type
    #respond NS
    dns_res['dns_resp_name'] = dns_resp_name
    #respond ipv4 adress
    dns_res['dns_a'] = dns_a
    #time to live
    dns_res['dns_resp_ttl'] = dns_resp_ttl

    return dns_res


