# 📡 Implementação do Protocolo RDT 3.0 via UDP

Este projeto consiste em uma aplicação de transferência confiável de dados utilizando o protocolo **RDT 3.0** sobre a camada de transporte UDP. Desenvolvido como requisito prático para a disciplina de Aplicações em Computadores (IFMA).

## 🚀 Principais Mecanismos
O protocolo foi projetado para lidar com as imperfeições do canal, implementando:

* **Verificação de Integridade**: Uso de **Checksum** para detectar se os bits da mensagem foram alterados durante a transmissão.
* **Controle de Sequência**: Alternância entre os bits **0 e 1** para garantir que o receptor identifique pacotes novos e descarte duplicatas.
* **Recuperação de Perdas**: Temporizador (**Timeout**) no lado do emissor que realiza a retransmissão automática caso a confirmação (ACK) não chegue a tempo.
* **Fluxo Stop-and-Wait**: Garante que o próximo pacote só seja enviado após a confirmação bem-sucedida do anterior.

---

## 🎮 Laboratório de Simulação
Para validar a robustez da implementação, o cliente dispõe de um menu interativo para simular cenários reais de falha:

1.  **Cenário Perfeito**: Envio e recebimento imediato sem interferências.
2.  **Cenário de Corrupção**: O cliente altera o checksum propositalmente. O servidor detecta a falha e descarta o pacote.
3.  **Cenário de Perda/Atraso**: O envio é retardado para forçar o estouro do cronômetro de timeout e demonstrar a retransmissão.

---

## 🛠️ Instruções de Uso

### 1. Inicialização do Servidor
Abra o terminal na pasta do projeto e execute o comando para deixar o receptor em modo de escuta:
```bash
python UDPServer.py

