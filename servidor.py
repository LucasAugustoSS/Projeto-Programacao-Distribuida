import socket
import threading
import json

def conexao(conn, addr):
    print(f"Conectado por {addr}")

    while True:
        dados = conn.recv(1024)
        if not dados:
            break

        print(f"Recebido: {dados.decode()}")

        estado_agente = json.loads(dados.decode())

        tipo = estado_agente.pop("tipo", None)

        if tipo == "pedido":
            pedido = estado_agente.pop("pedido", None)
            if pedido not in historico:
                historico[pedido] = {
                    "status atual": estado_agente,
                    "historico": []
                }

            historico[pedido]["historico"].append(estado_agente)

            conn.send(f"Pedido {pedido} atualizado".encode())
        elif tipo == "historico":
            conn.send(json.dumps(historico).encode())

    conn.close()
    print(f"Conexão por {addr} encerrada")

servidor = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

servidor.bind(('localhost', 12345))

servidor.listen(5)
print("Servidor aguardando...")

historico = {}

while True:
    conn, addr = servidor.accept()

    thread = threading.Thread(target=conexao, args=(conn, addr))
    thread.start()