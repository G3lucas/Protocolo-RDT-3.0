import socket
import time

PORTA_SERVIDOR = 5000

def checksum(mensagem):
    return sum(ord(c) for c in mensagem) % 256    

def iniciar_servidor():
    socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_udp.bind(("", PORTA_SERVIDOR))
   
    print(f"\n{'='*50}")
    print(f"  SERVIDOR RDT 3.0 ATIVO - Porta: {PORTA_SERVIDOR}")
    print(f"{'='*50}\n")
    
    seq_atual = 0

    while True:
        try:
            pacote, endereco_cliente = socket_udp.recvfrom(1024)
            mensagem = pacote.decode()
            try:
                campos = mensagem.split("|", 3)
                
                seq_recebido = int(campos[0])           
                checksum_recebido = int(campos[1])      
                delay_flag = int(campos[2])             
                conteudo = campos[3]                   
            except ValueError:
               
                print(f"[!] Pacote com formato inválido recebido: {mensagem}")
                continue 

            checksum_calculado = checksum(conteudo)
            print(f"\n[RX] Sequência: {seq_recebido} | Dados: '{conteudo}' | Checksum RX: {checksum_recebido}")

            if checksum_recebido != checksum_calculado:
                print(f"[X] DETECÇÃO DE ERRO - Checksum inválido!")
                print(f"    Esperado: {checksum_calculado} | Recebido: {checksum_recebido}")
                print("[*] Ação: Descartando pacote (sem confirmação)")
                continue 

            if delay_flag == 1:
                print("[WAIT] Aplicando delay de 5 segundos conforme solicitado...")
                time.sleep(5)  

            if seq_recebido == seq_atual:
                print(f"[OK] Pacote válido! Sequência correta: {seq_recebido}")
                print(f"[+] Processando mensagem: {conteudo}")
                
                confirmacao = f"ACK|{seq_atual}"
                
                socket_udp.sendto(confirmacao.encode(), endereco_cliente)
                print(f"[TX] Confirmação enviada: {confirmacao}")
                
                seq_atual = 1 - seq_atual

            else:
                print(f"[!] DUPLICATA DETECTADA!")
                print(f"    Esperado: {seq_atual} | Recebido: {seq_recebido}")
                print("[*] Reenviando última confirmação...")
    
                confirmacao = f"ACK|{seq_recebido}"
                socket_udp.sendto(confirmacao.encode(), endereco_cliente)

        except Exception as erro:
            print(f"[ERRO] Exceção capturada: {erro}")

iniciar_servidor()
