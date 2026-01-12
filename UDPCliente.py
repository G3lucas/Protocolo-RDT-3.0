import socket
import time
import random

# Configurações de onde o servidor está rodando
SERVER_IP = "localhost"
SERVER_PORT = 5000
TIMEOUT = 3.0  # Tempo máximo que o cliente espera pelo ACK antes de reenviar

# Inicialização do Socket (UDP)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(TIMEOUT) # Ativa o relógio de espera do socket

# Variável global de sequência (começa em 0, depois vai para 1)
seq = 0

# Função que gera um "código de segurança" (soma das letras) para ver se o dado mudou
def checksum(data):
    return sum(ord(c) for c in data) % 256

# Função que cria o menu de testes para você mostrar na apresentação
def menu():
    print("\n===== MENU DE SIMULAÇÃO DO CANAL =====")
    print("1 - Entrega normal")
    print("2 - Corromper dados (Altera Checksum)")
    print("3 - Inserir atraso artificial (Delay)")
   
    try:
        return int(input("Escolha o comportamento para este envio: "))
    except:
        return 1

# Função principal de envio de pacote
def send_packet(data):
    global seq
    
    # Calcula o checksum verdadeiro dos dados
    chk_real = checksum(data)
    
    # Pergunta qual teste você quer fazer agora
    opcao = menu()
    
    # Define se o checksum enviado será o real ou um errado
    chk_to_send = chk_real
    simular_delay = False
    
    # Se escolher 2, envia um valor fixo (999) para fingir erro
    if opcao == 2:
        print("[CLIENTE-SIMULAÇÃO] 🔨 Os dados serão enviados CORROMPIDOS (Checksum inválido).")
        chk_to_send = 999  # Valor propositalmente errado
    # Se escolher 3, marca que deve demorar para enviar
    elif opcao == 3:
        print("[CLIENTE-SIMULAÇÃO] ⏳ Um atraso será inserido antes do envio.")
        simular_delay = True
    else:
        print("[CLIENTE-SIMULAÇÃO] Envio normal.")

    # Loop principal (Fica aqui até receber o ACK correto)
    while True:
        # Monta a mensagem final: numero|checksum|texto
        pacote = f"{seq}|{chk_to_send}|{data}"
        
        # Se for simulação de delay, faz o programa "dormir" alguns segundos
        if simular_delay:
            delay = random.randint(2, 4)
            print(f"[CLIENTE] ...Dormindo por {delay}s simulando atraso...")
            time.sleep(delay)
            simular_delay = False # Garante que o atraso só ocorra na primeira tentativa

        print(f"\n[CLIENTE] Enviando pacote (Seq: {seq})...")
        print(f"          Dados: '{data}' | Checksum Enviado: {chk_to_send}")
        
        # Envia os bytes do pacote para o servidor
        sock.sendto(pacote.encode(), (SERVER_IP, SERVER_PORT))
        
        # Tenta receber a resposta do servidor
        try:
            recv_data, _ = sock.recvfrom(1024)
            ack_msg = recv_data.decode()
            
            print(f"[CLIENTE] Mensagem recebida: {ack_msg}")

            # Verifica se o que recebeu contém a palavra "ACK"
            if "ACK" in ack_msg:
                _, ack_seq_str = ack_msg.split("|")
                ack_seq = int(ack_seq_str)
                
                # Se o número do ACK for o esperado, termina este envio
                if ack_seq == seq:
                    print(f"[CLIENTE] ✅ ACK {ack_seq} Recebido com sucesso!")
                    # Inverte a sequência: 0 vira 1, ou 1 vira 0
                    seq = 1 - seq
                    break # Sai do loop 'while True'
                else:
                    print(f"[CLIENTE] ⚠️ ACK incorreto recebido (Esperado: {seq}, Veio: {ack_seq}). Ignorando.")
            
        except socket.timeout:
            # Se o tempo acabar e não chegar resposta, o loop recomeça e envia de novo
            print(f"[CLIENTE] ⏰ TIMEOUT! Não recebi ACK para Seq {seq}. Retransmitindo...")
            print(f"[CLIENTE] (Causa provável: Pacote corrompido/ignorado pelo servidor ou ACK perdido)")

# Início de tudo
print("=== CLIENTE RDT 3.0 INICIADO ===")
while True:
    msg = input("\nDigite a mensagem a ser enviada (ou 'sair'): ")
    if msg.lower() == 'sair':
        break
    send_packet(msg)