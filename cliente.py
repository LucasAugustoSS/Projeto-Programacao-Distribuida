import socket
import json
import time
import random

HOST = 'localhost'
PORTA = 12345

pendentes = []


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

    else:
        msg = {
            "tipo": "invalido"
        }

    return msg


def conectar():
    while True:
        try:
            cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cliente.connect((HOST, PORTA))
            print("Conectado ao servidor.")
            return cliente
        except ConnectionRefusedError:
            print("Servidor indisponível. Tentando reconectar em 3 segundos...")
            time.sleep(3)


def EnvioMsg(cliente, msg):
    try:
        cliente.send(json.dumps(msg).encode())
        return True
    except (BrokenPipeError, ConnectionResetError, OSError):
        return False


def RespostaS(cliente):
    try:
        resposta = cliente.recv(1024)
        if not resposta:
            return None
        return resposta.decode()
    except (ConnectionResetError, OSError):
        return None


def layoutResposta(cliente):
    try:
        cabecalho = cliente.recv(10)
        if not cabecalho:
            return None

        tamanho = int(cabecalho.decode().strip())
        dados = b""

        while len(dados) < tamanho:
            parte = cliente.recv(tamanho - len(dados))
            if not parte:
                return None
            dados += parte

        return dados.decode()

    except (ConnectionResetError, OSError, ValueError):
        return None


def SalvaNaFila(msg):
    pendentes.append(msg)
    print("Evento salvo na fila local.")


def ReenvioPendendes(cliente):
    global pendentes

    if not pendentes:
        return cliente

    print("\nTentando reenviar eventos pendentes...")

    nova_fila = []

    for evento in pendentes:
        enviado = EnvioMsg(cliente, evento)

        if not enviado:
            print("Falha ao reenviar evento. Reconectando...")
            try:
                cliente.close()
            except:
                pass
            cliente = conectar()
            nova_fila.append(evento)
            continue

        resposta = RespostaS(cliente)
        if resposta is None:
            print("Falha ao receber confirmação do evento pendente.")
            nova_fila.append(evento)
        else:
            print(f"Evento pendente reenviado com sucesso: {resposta}")

    pendentes = nova_fila
    return cliente


cliente = conectar()

while True:
    cliente = ReenvioPendendes(cliente)

    msg = requisicao()

    if msg["tipo"] == "invalido":
        print("Opção inválida.")
        continue

    if msg["tipo"] == "pedido":
        enviado = EnvioMsg(cliente, msg)

        if not enviado:
            print("Servidor indisponível no envio do pedido.")
            SalvaNaFila(msg)
            try:
                cliente.close()
            except:
                pass
            cliente = conectar()
            continue

        resposta = RespostaS(cliente)

        if resposta is None:
            print("Falha ao receber resposta do servidor.")
            SalvaNaFila(msg)
            try:
                cliente.close()
            except:
                pass
            cliente = conectar()
            continue

        print(f"Resposta: {resposta}")

        if resposta == "Pedido já realizado":
            continue

        tempo_previsto = 5
        tempo_entrega = random.randint(3, 6)

        while True:
            time.sleep(2)

            if tempo_entrega <= 0:
                msg_atualizada = {
                    "tipo": "pedido",
                    "pedido": msg["pedido"],
                    "status": "entregue",
                    "veiculo": msg["veiculo"]
                }
            elif tempo_previsto <= 0:
                msg_atualizada = {
                    "tipo": "pedido",
                    "pedido": msg["pedido"],
                    "status": "atrasado",
                    "veiculo": msg["veiculo"]
                }
            else:
                msg_atualizada = {
                    "tipo": "pedido",
                    "pedido": msg["pedido"],
                    "status": "em rota",
                    "veiculo": msg["veiculo"]
                }

            enviado = EnvioMsg(cliente, msg_atualizada)

            if not enviado:
                print("Servidor indisponível durante atualização.")
                SalvaNaFila(msg_atualizada)
                try:
                    cliente.close()
                except:
                    pass
                cliente = conectar()
                break

            resposta = RespostaS(cliente)

            if resposta is None:
                print("Falha ao receber confirmação da atualização.")
                SalvaNaFila(msg_atualizada)
                try:
                    cliente.close()
                except:
                    pass
                cliente = conectar()
                break

            print(f"Resposta: {resposta}")

            if msg_atualizada["status"] == "entregue":
                break

            tempo_entrega -= 1
            tempo_previsto -= 1

    elif msg["tipo"] == "status pedido":
        enviado = EnvioMsg(cliente, msg)

        if not enviado:
            print("Servidor indisponível. Não foi possível consultar o status agora.")
            try:
                cliente.close()
            except:
                pass
            cliente = conectar()
            continue

        resposta = layoutResposta(cliente)

        if resposta is None:
            print("Falha ao receber status.")
            try:
                cliente.close()
            except:
                pass
            cliente = conectar()
            continue

        print(resposta)

    elif msg["tipo"] == "historico":
        enviado = EnvioMsg(cliente, msg)

        if not enviado:
            print("Servidor indisponível. Não foi possível consultar o histórico agora.")
            try:
                cliente.close()
            except:
                pass
            cliente = conectar()
            continue

        resposta = layoutResposta(cliente)

        if resposta is None:
            print("Falha ao receber histórico.")
            try:
                cliente.close()
            except:
                pass
            cliente = conectar()
            continue

        print(json.loads(resposta))

    elif msg["tipo"] == "sair":
        break

cliente.close()
print("Conexão encerrada.")