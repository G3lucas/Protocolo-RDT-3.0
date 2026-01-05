import socket

SERVER_IP = "localhost"
PORTA = 5000

def checksum(data):
    return sum(ord(c) for c in data) % 256

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((SERVER_IP, PORTA))

    print(f" O servidor está aguardando na porta {PORTA}")
    
    expected_seq = 0

    while True:
        try:

            data_recv, addr = sock.recvfrom(1024)
            msg_decoded = data_recv.decode()

            try:
                seq_str, chk_str, content = msg_decoded.split("|", 2)
                seq_recv = int(seq_str)
                chk_recv = int(chk_str)
            except ValueError:
                print(f"\n[Server] Erro no pacote: {msg_decoded}")
                continue

            chk_calc = checksum(content)

            print(f"\n[Server] Recebido Sequencia={seq_recv} | ChecksumRecebido={chk_recv} | dados='{content}'")


            if chk_recv != chk_calc:
                print(f"[Server] pacote comrrompido! (Calc: {chk_calc} != Recv: {chk_recv})")
                print("[Server]  Ignorar pacote ou seja não enviar o ACK.")
                continue

            if seq_recv == expected_seq:
                print(f"[Server] Pacote íntegro ({seq_recv}).")
                print(f"[Server] dados processados: {content}")
                
                ack_packet = f"ACK|{expected_seq}"
                sock.sendto(ack_packet.encode(), addr)
                print(f"[Server] Encaminhado: {ack_packet}")

                expected_seq = 1 - expected_seq
            
            else:

                print(f"[Server] Pacote Duplicado (Ele esperava {expected_seq}, porem veio {seq_recv}).")
                print(f"[Server] Reenviar ACK ({seq_recv}).")
                ack_packet = f"ACK|{seq_recv}"
                sock.sendto(ack_packet.encode(), addr)

        except Exception as e:
            print(f"[Erro] {e}")

if __name__ == "__main__":
    main()