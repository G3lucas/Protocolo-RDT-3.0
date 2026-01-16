import socket
import time

IP_DESTINO = "localhost"        
PORTA_SERVIDOR = 5000             
TEMPO_LIMITE = 3.0               


def calcular_checksum(texto):  
    return sum(ord(c) for c in texto) % 256

def executar_cliente():
    socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_udp.settimeout(TEMPO_LIMITE)
   
    numero_sequencia = 0

    print(f"\n{'='*50}")
    print(f"  CLIENTE RDT 3.0")
    print(f"  Servidor: {IP_DESTINO}:{PORTA_SERVIDOR}")
    print(f"  Timeout: {TEMPO_LIMITE}s")
    print(f"{'='*50}\n")

    while True:
        entrada = input(">>> Digite mensagem (ou 's' para sair): ")
        if entrada.lower() == 's':
            print("\n[*] Encerrando cliente...")
            break  

        print("\n[OPÇÕES DE ENVIO]")
        print("  1 - Envio Normal (sem problemas)")
        print("  2 - Simular Corrupção de Dados")
        print("  3 - Simular Atraso na Resposta")
        escolha_usuario = input(">>> Selecione: ")

        checksum_msg = calcular_checksum(entrada) 
        sinalizador_atraso = 0                     
        
        if escolha_usuario == "2":
            checksum_msg = 888
        
        elif escolha_usuario == "3":
            sinalizador_atraso = 1

        payload = f"{numero_sequencia}|{checksum_msg}|{sinalizador_atraso}|{entrada}"

        tentativa = 0
        while True:
            tentativa += 1
            print(f"\n[ENVIO - Tentativa {tentativa}]")
            print(f"  Seq: {numero_sequencia} | Atraso: {sinalizador_atraso}")
            socket_udp.sendto(payload.encode(), (IP_DESTINO, PORTA_SERVIDOR))
            
            try:
                resposta, _ = socket_udp.recvfrom(1024)
                msg_ack = resposta.decode()
                print(f"[RX] Resposta: {msg_ack}")

                if f"ACK|{numero_sequencia}" in msg_ack:
                    print(f"[SUCESSO] Mensagem confirmada!")
                    print(f"[*] Alternando sequência: {numero_sequencia} -> {1 - numero_sequencia}\n")
                    
                    numero_sequencia = 1 - numero_sequencia
                    break
            
            except socket.timeout:
                print(f"[TIMEOUT] Nenhuma resposta em {TEMPO_LIMITE}s")
                print(f"[*] Reenviando... aguarde\n")
            
if __name__ == "__main__":
    executar_cliente()
