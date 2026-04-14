import socket
import threading
import json
from time import time
from datetime import datetime

def conexao(conn, addr):
    print(f"Conectado por {addr}")

    while True:
        dados = conn.recv(1024)
        if not dados:
            break

        print(f"Recebido: {dados.decode()}")

        estado_agente = json.loads(dados.decode())
        estado_agente["horario"] = f"{datetime.now()}"
        tipo = estado_agente.pop("tipo", None)
        msg = "-"
        tamanho = b""

        with lock:
            if tipo == "pedido":
                pedido = estado_agente.pop("pedido", None)

                if pedido not in historico:
                    tempo_inicio = time()
                    historico[pedido] = {
                        "status atual": estado_agente["status"],
                        "historico": [estado_agente]
                    }
                    msg = f"{pedido} em coleta...".encode()
                elif estado_agente["status"] != "coletando":
                    historico[pedido]["status atual"] = estado_agente["status"]
                    historico[pedido]["historico"].append(estado_agente)

                    status_anterior = historico[pedido]["historico"][-2]["status"]

                    if (estado_agente["status"] == "em rota" and
                        status_anterior == "coletando"):
                        msg = f"{pedido} em rota..."
                    elif (estado_agente["status"] == "atrasado" and
                          status_anterior == "em rota"):
                        msg = f"{pedido} atrasado..."
                    elif estado_agente["status"] == "entregue":
                        tempo_fim = time()
                        tempo_total = round(tempo_fim - tempo_inicio, 2)
                        msg = f"{pedido} entregue em {tempo_total}s."
                    msg = msg.encode()
                else:
                    msg = "Pedido já realizado".encode()

            elif tipo == "status pedido":
                pedido = estado_agente.pop("pedido", None)
                
                if pedido not in historico:
                    status = "não encontrado"
                else:
                    status = historico[pedido]["status atual"]

                msg = f"Status de {pedido}: {status}\nHorário: {datetime.now()}".encode()
                tamanho = f"{len(msg):<10}".encode()

            elif tipo == "historico":
                msg = json.dumps(historico).encode()
                tamanho = f"{len(msg):<10}".encode()

            conn.send(tamanho + msg)

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
lock = threading.Lock()

while True:
    conn, addr = servidor.accept()

    thread = threading.Thread(target=conexao, args=(conn, addr))
    thread.start()