import socket
import json

def requisicao():
    print(
        "1. Enviar Pedido\n" +
        "2. Ver Histórico\n" +
        "3. Sair"
    )
    numero = input("> ")

    if numero == "1":
        numero_pedido = input("Número do pedido: ")

        msg = {
            "tipo": "pedido",
            "pedido": f"pedido {numero_pedido}",
            "status": "em rota",
            "veiculo": 1
        }
    elif numero == "2":
        msg = {
            "tipo": "historico"
        }
    elif numero == "3":
        return numero

    return msg

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
    cliente.connect(('localhost', 12345))

    while True:
        msg = requisicao()
        if msg == "3":
            break

        cliente.send(json.dumps(msg).encode())

        resposta = cliente.recv(1024)
        print(f"Resposta: {resposta.decode()}")

print("Conexão encerrada.")