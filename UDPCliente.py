import socket
import time

# Configuracoes de rede
IP_ALVO = "127.0.0.1"
PORTA_ALVO = 5000
TEMPO_LIMITE = 3.0 # Segundos do cronometro

def calcular_checksum(texto):
    # Soma simples para verificar erros
    return sum(ord(c) for c in texto) % 256

def menu_de_testes():
    print("\n--- COMO QUER ENVIAR? ---")
    print("1. Enviar normal (Sem erros)")
    print("2. Corromper mensagem (Erro de Checksum)")
    print("3. Forcar atraso (Vai dar Timeout)")
    return input("Escolha a opcao: ")

def iniciar_cliente():
    # Cria o socket e define o tempo de espera
    cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cliente.settimeout(TEMPO_LIMITE)

    # RDT 3.0: Comeca com o pacote 0
    seq_atual = 0

    while True:
        txt = input("\nEscreva sua mensagem (ou 'parar'): ")
        if txt.lower() == 'parar': break

        opcao = menu_de_testes()
        
        chk = calcular_checksum(txt)
        atraso_manual = 0

        # Aplica as falhas para mostrar ao professor
        if opcao == "2":
            print(">> Alterando o checksum para gerar erro...")
            chk = chk + 1 
        elif opcao == "3":
            print(">> Aplicando atraso artificial...")
            atraso_manual = TEMPO_LIMITE + 1 # Faz o cliente demorar mais que o timeout

        pacote = f"{seq_atual}|{chk}|{txt}"
        confirmado = False

        # Loop do protocolo Stop-and-Wait
        while not confirmado:
            try:
                if atraso_manual > 0:
                    time.sleep(atraso_manual)
                    atraso_manual = 0 # Reseta para o reenvio ser normal

                print(f"[ENVIO] Mandando Pacote {seq_atual}...")
                cliente.sendto(pacote.encode(), (IP_ALVO, PORTA_ALVO))

                # Espera a resposta (ACK)
                dados_ack, _ = cliente.recvfrom(1024)
                res_ack = dados_ack.decode()

                if res_ack == f"ACK|{seq_atual}":
                    print(f"[SUCESSO] {res_ack} recebido!")
                    confirmado = True
                    seq_atual = 1 - seq_atual # Alterna entre 0 e 1
            
            except socket.timeout:
                print(f"[TIMEOUT] Nao recebi o ACK! Reenviando pacote {seq_atual}...")
            except ConnectionResetError:
                print("[ERRO] Ligue o servidor primeiro!")
                break

    cliente.close()

if __name__ == "__main__":
    iniciar_cliente()