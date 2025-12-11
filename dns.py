import socket, glob, json

port = 53
ip = '127.0.0.1'

# Arg one: We want to use IPV4. Arg two: We are using UDP protocol
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip, port))

def load_zone():
    json_zone = {} 
    zone_files = glob.glob('zones/*.zone')      # Look into a zone folder for every file that ends with a .zone

    for zone in zone_files:
        with open(zone) as zone_data:
            data = json.load(zone_data)
            zone_name = data["$origin"].rstrip('.')
            json_zone[zone_name] = data
    return json_zone

zone_data = load_zone()

def get_zone(domain):
    global zone_data

    zone_name = '.'.join(domain).rstrip('.')
    return zone_data[zone_name]

def build_question(domain_name, rec_type):
    qbytes = b''

    for part in domain_name:
        qbytes += bytes([len(part)])

        for char in part:
            qbytes += ord(char).to_bytes(1, byteorder='big')

    if rec_type == 'a':
        qbytes += (1).to_bytes(2, byteorder='big')

    qbytes += (1).to_bytes(2, byteorder='big')

    return qbytes

def get_recs(data):
    domain, question_type = get_question_domain(data)
    qt = ''
    if question_type == b'\x00\x01':
        qt = 'a'
    zone = get_zone(domain)
    return (zone[qt], qt, domain)

def rec_to_bytes(domain_name, rec_type, rec_ttl, rec_val):
    rbytes = b'\xc0\x0c'            # Pointer to name in our question

    # Type A
    rbytes += (0).to_bytes(1, 'big') + (1).to_bytes(1, 'big')
    # Class in
    rbytes += (0).to_bytes(1, 'big') + (1).to_bytes(1, 'big')
    # TTL
    rbytes += int(rec_ttl).to_bytes(4, 'big')

    if rec_type == 'a':
        rbytes += (0).to_bytes(1, 'big') + (4).to_bytes(1, 'big')
        for part in rec_val.split('.'):
            rbytes += bytes([int(part)])
    return rbytes

def get_question_domain(data):
    state = 0
    expected_length = 0
    domain_string = ''
    domain_parts = []
    x = 0
    y = 0

    for byte in data:
        if state == 1:
            if byte != 0:
                domain_string += chr(byte)
            x += 1
            if x == expected_length:
                domain_parts.append(domain_string)
                domain_string = ''
                state = 0
                x = 0
            if byte == 0:
                domain_parts.append(domain_string)
                break
        else:
            state = 1
            expected_length = byte
        y += 1

    question_type = data[y : y + 2]
    return (domain_parts, question_type)

def get_flags(_flags):
    return b'\x84\x00'         # Hardcoded answer      

def build_response(data):

    # Get transaction ID
    transaction_id = data[:2] # Get 0 - 2 bytes
    records, rec_type, domain_name = get_recs(data[12:])
    # Get the flags
    flags = get_flags(data[2:4])
    
    # Question count
    QDCOUNT = (1).to_bytes(2, 'big')                              # A count of 1 in two byte

    # Answer count                  
    ANCOUNT = len(records).to_bytes(2,'big')
    # Nameserver count
    NSCOUNT = (0).to_bytes(2, 'big')
    # Additional count
    ARCOUNT = (0).to_bytes(2, 'big')
    dns_header = transaction_id + flags + QDCOUNT + ANCOUNT + NSCOUNT + ARCOUNT
    # DNS body
    dns_body = b''
    dns_question = build_question(domain_name, rec_type)

    # Answer to the question
    for record in records:
        dns_body += rec_to_bytes(domain_name, rec_type, record["ttl"], record["value"])
    return dns_header + dns_question + dns_body

while True:
    data, addr = sock.recvfrom(512) # Assuming that every request is <= 512 bytes
    response = build_response(data)
    sock.sendto(response, addr)