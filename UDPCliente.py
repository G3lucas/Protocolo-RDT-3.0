import socket
import time
import random

# Configurações de rede
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000
TIMEOUT_VALUE = 3.0  # Tempo limite para o ACK chegar

def calcular_checksum(texto):
    """Calcula a soma de verificação simples"""
    return sum(ord(c) for c in texto) % 256

def send_packet(data):
    # Variáveis globais de controle do protocolo RDT 3.0
    global seq
    
    # Menu de simulação de falhas (Exigência do Professor)
    print("\n--- TESTAR CANAL ---")
    print("1. Enviar normal")
    print("2. Corromper mensagem (Checksum)")
    print("3. Inserir atraso (Timeout)")
    opcao = input("Escolha uma opção: ")

    chk_to_send = calcular_checksum(data)
    simular_delay = False

    # Aplica as falhas do RDT 3.0
    if opcao == "2":
        print("[CLIENTE] >> Avacalhando o checksum...")
        chk_to_send += 1
    elif opcao == "3":
        print("[CLIENTE] >> Ativando simulação de atraso...")
        simular_delay = True

    # Loop de retransmissão (Stop-and-Wait)
    while True:
        # Monta o pacote: seq|checksum|dados
        pacote = f"{seq}|{chk_to_send}|{data}"
        
        # Aplica o atraso se solicitado (simula latência ou perda)
        if simular_delay:
            delay = random.randint(4, 6) # Maior que o TIMEOUT_VALUE
            print(f"[CLIENTE] ...Dormindo por {delay}s simulando atraso...")
            time.sleep(delay)
            simular_delay = False # Reseta para a retransmissão ser normal

        print(f"\n[CLIENTE] Enviando pacote (Seq: {seq})...")
        print(f"          Dados: '{data}' | Checksum: {chk_to_send}")
        
        sock.sendto(pacote.encode(), (SERVER_IP, SERVER_PORT))
        
        # Estado: Aguardando ACK
        try:
            # Tenta receber resposta
            recv_data, _ = sock.recvfrom(1024)
            ack_msg = recv_data.decode()
            
            print(f"[CLIENTE] Mensagem recebida do servidor: {ack_msg}")

            if "ACK" in ack_msg:
                _, ack_seq_str = ack_msg.split("|")
                ack_seq = int(ack_seq_str)
                
                # Verifica se é o ACK esperado
                if ack_seq == seq:
                    print(f"[CLIENTE] ✅ ACK {ack_seq} Recebido com sucesso!")
                    # Alterna sequência para o próximo pacote (0 -> 1 ou 1 -> 0)
                    seq = 1 - seq
                    break # Sai do loop de retransmissão e volta para o input principal
                else:
                    print(f"[CLIENTE] ⚠️ ACK incorreto (Esperado: {seq}, Veio: {ack_seq}). Ignorando.")
            
        except socket.timeout:
            # Timeout estourou: Retransmitir
            print(f"[CLIENTE] ⏰ TIMEOUT! Não recebi ACK para Seq {seq}. Retransmitindo...")

# --- INÍCIO DO PROGRAMA ---
print("=== CLIENTE RDT 3.0 INICIADO ===")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(TIMEOUT_VALUE)
seq = 0 # Começa no estado de envio do pacote 0

while True:
    msg = input("\nDigite a mensagem a ser enviada (ou 'sair'): ")
    if msg.lower() == 'sair':
        print("Encerrando...")
        break
    send_packet(msg)

sock.close()