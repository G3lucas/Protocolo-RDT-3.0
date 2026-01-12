import socket

# Configuração simples da porta
MINHA_PORTA = 5000

# Função para ver se a mensagem chegou inteira (Checksum)
def checar_mensagem(texto):
    return sum(ord(letra) for letra in texto) % 256

def rodar_servidor():
    # Cria o socket UDP (padrão para RDT)
    servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    servidor.bind(("", MINHA_PORTA))

    print(f"--- SERVIDOR ONLINE (Porta {MINHA_PORTA}) ---")
    
    # RDT 3.0: Começa esperando o pacote zero
    proximo_pacote = 0

    while True:
        # Recebe os dados brutos e o endereço de quem enviou
        pacote_bruto, endereco_cliente = servidor.recvfrom(1024)
        msg_recebida = pacote_bruto.decode()
        
        # O cliente manda no formato: sequencia|checksum|texto
        partes = msg_recebida.split("|", 2)
        num_seq = int(partes[0])
        check_cliente = int(partes[1])
        conteudo = partes[2]

        print(f"\n[RECEBIDO] Pacote {num_seq}: '{conteudo}'")

        # 1. Verifica se a mensagem corrompeu (Checksum)
        check_calculado = checar_mensagem(conteudo)
        
        if check_cliente != check_calculado:
            print("[ERRO] Checksum errado! Pacote corrompido. Ignorando...")
            continue # Se estiver errado, o servidor não manda ACK [cite: 11]

        # 2. Verifica se é o pacote na ordem certa
        if num_seq == proximo_pacote:
            print(f"[OK] Pacote {num_seq} correto. Enviando confirmação (ACK)...")
            
            confirmacao = f"ACK|{num_seq}"
            servidor.sendto(confirmacao.encode(), endereco_cliente)
            
            # Alterna o estado: 0 vira 1, 1 vira 0 [cite: 16]
            proximo_pacote = 1 - proximo_pacote
        else:
            # Se receber um repetido, manda o ACK de novo para destravar o cliente
            print(f"[AVISO] Pacote {num_seq} repetido. Reenviando ACK.")
            confirmacao = f"ACK|{num_seq}"
            servidor.sendto(confirmacao.encode(), endereco_cliente)

if __name__ == "__main__":
    rodar_servidor()