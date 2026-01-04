import socket


SERVER_IP = "localhost"
PORTA = 5000

def checksum(data):
    
    return sum(ord(c) for c in data) % 256

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((SERVER_IP, PORTA))

    print(f"SERVIDOR RDT 3.0 AGUARDANDO NA PORTA {PORTA} ===")

    expected_seq = 0