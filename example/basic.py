import heka
import socket


msg = heka.Message(
    'ads_served',
    'ads_server',
    heka.INFO,
    {'ad_ids': [1, 2, 3]}
)

payload = msg.encode()
print(repr(payload))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(payload, ('localhost', heka.DEFAULT_PORT))
