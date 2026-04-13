import socket
import json
import time
import random

def requisicao():
    print(
        "1. Enviar Pedido\n" +
        "2. Status de Pedido\n" +
        "3. Ver Histórico\n" +
        "4. Sair"
    )
    numero = input("> ")

    if numero == "1":
        numero_pedido = input("Número do pedido: ")

        msg = {
            "tipo": "pedido",
            "pedido": f"pedido {numero_pedido}",
            "status": "coletando",
            "veiculo": 1
        }
    elif numero == "2":
        numero_pedido = input("Número do pedido: ")

        msg = {
            "tipo": "status pedido",
            "pedido": f"pedido {numero_pedido}"
        }
    elif numero == "3":
        msg = {
            "tipo": "historico"
        }
    elif numero == "4":
        msg = {
            "tipo": "sair"
        }

    return msg

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
    cliente.connect(('localhost', 12345))

    while True:
        msg = requisicao()

        if msg["tipo"] == "pedido":
            cliente.send(json.dumps(msg).encode())
            resposta = cliente.recv(1024)
            print(f"Resposta: {resposta.decode()}")

            if resposta.decode() == "Pedido já realizado":
                continue

            tempo_previsto = 5
            tempo_entrega = random.randint(3,6)

            while True:
                time.sleep(2)

                if tempo_entrega <= 0:
                    msg["status"] = "entregue"
                elif tempo_previsto <= 0:
                    msg["status"] = "atrasado"
                else:
                    msg["status"] = "em rota"

                cliente.send(json.dumps(msg).encode())
                resposta = cliente.recv(1024)
                print(f"Resposta: {resposta.decode()}")

                if msg["status"] == "entregue":
                    break

                tempo_entrega -= 1
                tempo_previsto -= 1

        elif msg["tipo"] == "status pedido" or msg["tipo"] == "historico":
            cliente.send(json.dumps(msg).encode())
            tamanho = int(cliente.recv(10).decode().strip())

            dados = b""
            while len(dados) < tamanho:
                restante = tamanho - len(dados)
                parte = cliente.recv(restante)

                if not parte:
                    break

                dados += parte

            print(f"{json.loads(dados.decode())}")

        elif msg["tipo"] == "sair":
            break

print("Conexão encerrada.")