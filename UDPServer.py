import socket

# Define a porta que o servidor ficará "ouvindo"
SERVER_PORT = 5000

# Função de Checksum: soma os valores das letras para conferir a integridade
def checksum(data):
    return sum(ord(c) for c in data) % 256

def main():
    # Cria o socket UDP (DGRAM) e vincula à porta 5000
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", SERVER_PORT))

    print(f"=== SERVIDOR RDT 3.0 AGUARDANDO NA PORTA {SERVER_PORT} ===")
    
    # O protocolo RDT 3.0 alterna entre 0 e 1. Começamos esperando o 0.
    seq_esperada = 0

    while True:
        try:
            # Recebe o pacote vindo do cliente (até 1024 bytes)
            data_recv, addr = sock.recvfrom(1024)
            msg_decoded = data_recv.decode()
            
            # Divide o texto recebido nos 3 pedaços usando a barra "|" como separador
            try:
                seq_str, chk_str, dados = msg_decoded.split("|", 2)
                seq_recebida = int(seq_str)
                check_recebido = int(chk_str)
            except ValueError:
                # Se a mensagem vier fora do formato "0|123|texto", cai aqui
                print(f"\n[SERVIDOR] Erro de formatação no pacote: {msg_decoded}")
                continue

            # O servidor faz o cálculo dele para ver se bate com o que o cliente mandou
            check_calc = checksum(dados)

            print(f"\n[SERVIDOR] Recebido: Seq={seq_recebida} | Dados='{dados}' | ChecksumRecebido={check_recebido}")

            # 1. TESTE DE CORRUPÇÃO: Se o cálculo for diferente do enviado, o dado "estragou"
            if check_recebido != check_calc:
                print(f"[SERVIDOR] ❌ PACOTE CORROMPIDO DETECTADO! (Calc: {check_calc} != Recv: {check_recebido})")
                print("[SERVIDOR] Ação: Ignorar pacote (não enviar ACK).")
                # No RDT 3.0, se está corrompido, o servidor ignora e o cliente reenvia por timeout
                continue
            
            # 2. TESTE DE SEQUÊNCIA: Verifica se é o pacote que ele estava esperando (0 ou 1)
            if seq_recebida == seq_esperada:
                print(f"[SERVIDOR] ✅ Pacote íntegro e na sequência correta ({seq_recebida}).")
                print(f"[SERVIDOR] Processando dados: {dados}")
                
                # Prepara o "Recibo" (ACK) para o cliente saber que deu tudo certo
                pacote_ack = f"ACK|{seq_esperada}"
                sock.sendto(pacote_ack.encode(), addr)
                print(f"[SERVIDOR] Enviado: {pacote_ack}")
                
                # Alterna o estado: se era 0, agora espera o 1. Se era 1, espera o 0.
                seq_esperada = 1 - seq_esperada

            else:
                # Se chegar um pacote que ele já recebeu (duplicado), ele reenvia o ACK
                # Isso acontece se o ACK anterior se perdeu no caminho.
                print(f"[SERVIDOR] ⚠️ Pacote Duplicado (Esperava {seq_esperada}, veio {seq_recebida}).")
                print(f"[SERVIDOR] Ação: Reenviar ACK do pacote recebido ({seq_recebida}).")
                pacote_ack = f"ACK|{seq_recebida}"
                sock.sendto(pacote_ack.encode(), addr)

        except Exception as e:
            print(f"[Erro] {e}")

# Inicia a função principal
main()