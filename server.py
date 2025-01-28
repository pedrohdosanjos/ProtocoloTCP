import socket
import threading
import hashlib
import os

# Configurações do servidor: definimos o endereço e a porta para conexão.
# REQUISITO: Escolher uma porta maior que 1024.
HOST = "127.0.0.1"  # Endereço localhost
PORT = 12345  # Porta para conexão, maior que 1024.


# Função para calcular o hash SHA-256 de um arquivo.
# REQUISITO: Calcular o hash (SHA) do arquivo enviado para verificar integridade.
def calcular_hash(filepath):
    sha256 = hashlib.sha256()  # Utiliza a função de hash SHA-256.
    with open(filepath, "rb") as f:
        # Lê o arquivo em chunks para evitar problemas com arquivos grandes (>10MB).
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()  # Retorna o hash hexadecimal.


# Função para tratar cada cliente.
# REQUISITO: Criar uma thread para lidar com cada cliente conectado.
def handle_client(conn, addr):
    print(f"Cliente conectado: {addr}")  # Confirma a conexão do cliente.
    try:
        while True:
            # Recebe dados do cliente.
            data = conn.recv(1024).decode()  # Limite de 1024 bytes por vez.
            if (
                not data or data.lower() == "sair"
            ):  # REQUISITO: Tratar o comando "Sair".
                print(f"Cliente {addr} desconectado.")  # Mensagem ao servidor.
                break  # Finaliza a thread.

            elif data.startswith("Arquivo"):
                # REQUISITO: Tratar a requisição de envio de arquivos.
                # O cliente solicita um arquivo no formato "Arquivo <NOME.EXT>".

                # Extrai o nome do arquivo solicitado.
                _, filename = data.split(" ", 1)
                if os.path.exists(filename):  # Verifica se o arquivo existe.
                    filesize = os.path.getsize(filename)  # Obtém o tamanho do arquivo.
                    filehash = calcular_hash(filename)  # Calcula o hash SHA-256.

                    # REQUISITO: Enviar o protocolo definido.
                    # Cabeçalho: <NOME_DO_ARQUIVO>|<TAMANHO>|<HASH>|<STATUS>.
                    conn.send(f"{filename}|{filesize}|{filehash}|ok".encode())

                    # Envia os dados do arquivo em chunks de 4096 bytes.
                    with open(filename, "rb") as f:
                        while chunk := f.read(4096):
                            conn.send(chunk)
                    print(f"Arquivo '{filename}' enviado para {addr}.")
                else:
                    # Caso o arquivo não exista, envia uma mensagem de erro.
                    conn.send(
                        "Erro|Arquivo inexistente.".encode()
                    )  # REQUISITO: Tratar arquivo inexistente.

            elif data.lower() == "chat":
                # REQUISITO: Implementar a funcionalidade de chat.
                print(f"Cliente {addr} entrou no modo Chat.")

                # Função para receber mensagens do cliente em tempo real.
                def receber_mensagens():
                    while True:
                        try:
                            msg = conn.recv(
                                1024
                            ).decode()  # Recebe mensagem do cliente.
                            if msg.lower() == "sair":  # Cliente encerra o chat.
                                print(f"Cliente {addr} encerrou o chat.")
                                break
                            print(
                                f"Cliente {addr} diz: {msg}"
                            )  # Imprime mensagem no servidor.
                        except:
                            break

                # Thread para gerenciar mensagens recebidas do cliente.
                thread_receber = threading.Thread(target=receber_mensagens)
                thread_receber.start()

                # Servidor envia mensagens para o cliente.
                while True:
                    try:
                        mensagem = input("")  # Entrada do servidor.
                        conn.send(mensagem.encode())  # Envia ao cliente.
                        if mensagem.lower() == "sair":  # Servidor encerra o chat.
                            print(f"Chat com cliente {addr} encerrado.")
                            break
                    except:
                        break
            else:
                # Resposta para comandos inválidos.
                conn.send("Comando inválido.".encode())
    except Exception as e:
        print(f"Erro com o cliente {addr}: {e}")  # Exibe erros no servidor.
    finally:
        conn.close()  # Fecha a conexão ao finalizar a thread.


# Função principal para iniciar o servidor.
# REQUISITO: Aceitar conexões de 2 clientes simultaneamente.
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Criação do socket TCP.
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Reutilizar a porta.
    server.bind((HOST, PORT))  # Associa o endereço e a porta.
    server.listen(2)  # Permite até 2 conexões simultâneas.
    print(f"Servidor rodando em {HOST}:{PORT}...")

    try:
        while True:
            # Aguarda por conexões de clientes.
            conn, addr = server.accept()  # Aceita conexão.
            # Cria uma thread para atender cada cliente.
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
    except KeyboardInterrupt:
        print("Servidor encerrado.")  # Permite finalizar com Ctrl+C.
        return 0
    finally:
        server.close()  # Fecha o socket ao encerrar.


if __name__ == "__main__":
    start_server()
