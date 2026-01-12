import socket
import time

# Configurações iniciais de rede
IP_DO_SERVIDOR = "localhost" # Endereço do computador destino
PORTA_DO_SERVIDOR = 5000     # Porta de entrada do servidor
TEMPO_LIMITE_TIMEOUT = 3.0   # Segundos que o cliente espera antes de retransmitir

def calcular_checksum(conteudo): # Função para criar o código de segurança
    # Soma os valores das letras para verificar se o dado foi alterado
    return sum(ord(letra) for letra in conteudo) % 256

def main():
    # Cria o transmissor e ativa o cronômetro para evitar perdas
    meu_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    meu_socket.settimeout(TEMPO_LIMITE_TIMEOUT)
    
    # Controla a ordem das mensagens (alterna entre 0 e 1)
    bit_ordem = 0 

    while True:
        mensagem_usuario = input("\nEscreva sua mensagem (ou 's' para sair): ")
        if mensagem_usuario.lower() == 's': break

        # Menu para escolher o teste durante a apresentação
        print("\n--- TESTES DE REDE ---")
        print("1. Envio Direto\n2. Provocar Erro de Checksum\n3. Provocar Atraso")
        escolha = input("Selecione uma opção: ")

        valor_verificador = calcular_checksum(mensagem_usuario) # Checksum correto
        ativar_delay = 0 # 0 é normal, 1 pede para o servidor demorar

        if escolha == "2":
            valor_verificador = 999 # Valor errado para o servidor detectar erro
            print("-> Enviando com Checksum propositalmente incorreto...")
        elif escolha == "3":
            ativar_delay = 1 # Comando para o servidor simular lentidão
            print("-> Enviando com solicitação de atraso na resposta...")

        # Monta o pacote: bit_ordem | checksum | flag_atraso | mensagem
        pacote_pronto = f"{bit_ordem}|{valor_verificador}|{ativar_delay}|{mensagem_usuario}"

        # Loop de Retransmissão: Tenta entregar até receber a confirmação (ACK)
        while True:
            print(f"-> Tentando entregar Pacote {bit_ordem}...") 
            meu_socket.sendto(pacote_pronto.encode(), (IP_DO_SERVIDOR, PORTA_DO_SERVIDOR))
            
            try:
                # Tenta receber a resposta do servidor
                confirmacao_bruta, _ = meu_socket.recvfrom(1024)
                msg_confirmacao = confirmacao_bruta.decode()
                print(f"-> Recebido do Servidor: {msg_confirmacao}")

                # Verifica se o servidor confirmou o pacote correto
                if f"ACK|{bit_ordem}" in msg_confirmacao:
                    print("-> ✅ MENSAGEM ENTREGUE! Trocando sequência.")
                    bit_ordem = 1 - bit_ordem # Muda de 0 para 1 (ou vice-versa)
                    break # Sai das tentativas e volta para o início
            
            except socket.timeout:
                # Se o servidor demorar mais que o limite, reenvia
                print("-> ⏰ TEMPO ESGOTADO! Sem sinal do servidor. Tentando novamente...")

if __name__ == "__main__":
    main()