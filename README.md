# Computer-Networks Final Project
## Summary
In this project, we created a simple authoriative DNS server in Python, completed with our own zone files which stores records for domains. The DNS runs locally running on UDP protocols. In another terminal, we use the command ```dig [domain-name]@127.0.0.1``` to see the packets it recieves from the DNS code. 

## Function definitions
* Opens an UDP socket on port 53
* For each packet recieved: 'build_response(data)' will send a reply back to the client in another terminal
* 'load_zone' looks inside the 'zones' folder with files that end with .zone then 'zone_data' will store the parsed data in a list
* 'get_question_domain' Reads from QNAME starting at byte 12 of the packet and builds the 'domain_parts' list to ["google", "com"]
* 'get_recs' will get the records, supporting only 'A' query types. After, it will look up records matching from the zone file
* 'build_question' will append query type and query class, reconstructing the original query name
* 'rec_to_bytes' Uses a pointer to reference the query name
* 'get_flags' returns a hard-coded flag for simplicity 
* 'build_response' Copies the first two bytes (transaction id) and builds the header of the packet

## Project Setup
Open a terminal and enter:
```sudo python3 dns.py```
to run the dns file.
Open another terminal and enter:
```dig google.com @127.0.0.1``` 
to see the program working in action.
If the dig command does not work, run:
```sudo apt install dnsutils -y```


## Source:
Credits to howCode's tutorial on
[YouTube](https://www.youtube.com/@howCode) & their [GitHub](https://github.com/howCodeORG/howDNS) on this project.

