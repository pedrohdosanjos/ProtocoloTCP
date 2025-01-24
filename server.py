import socket
import threading
import os
import hashlib

# Configurações do servidor
HOST = "127.0.0.1"  # Endereço localhost
PORT = 12345  # Porta maior que 1024


def calcular_hash(filepath):
    """Calcula o hash SHA-256 de um arquivo."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def handle_client(conn, addr):
    """Função para tratar a conexão com um cliente."""
    print(f"Cliente conectado: {addr}")
    while True:
        try:
            data = conn.recv(1024).decode()  # Recebe dados do cliente
            if not data:
                break

            if data.lower() == "sair":
                print(f"Cliente {addr} desconectado.")
                break

            elif data.startswith("Arquivo"):
                # Cabeçalho:
                # O servidor envia <NOME_DO_ARQUIVO>|<TAMANHO_DO_ARQUIVO>|<HASH_DO_ARQUIVO>|<STATUS>.
                # Exemplo: exemplo.txt|10485760|abc123def456|ok.

                # Dados:
                # Após o cabeçalho, o servidor envia os dados do arquivo em chunks de 4096 bytes.

                # Cliente:
                # Recebe o cabeçalho, verifica integridade pelo hash e salva o arquivo localmente.

                # Extrai o nome do arquivo solicitado
                _, filename = data.split(" ", 1)
                if os.path.exists(filename):
                    filesize = os.path.getsize(filename)
                    filehash = calcular_hash(filename)

                    # Envia o cabeçalho com os metadados
                    conn.send(f"{filename}|{filesize}|{filehash}|ok".encode())

                    # Envia os dados do arquivo em chunks
                    with open(filename, "rb") as f:
                        while chunk := f.read(4096):
                            conn.send(chunk)
                    print(f"Arquivo '{filename}' enviado para {addr}.")
                else:
                    # Envia mensagem de erro caso o arquivo não exista
                    conn.send(f"Erro|Arquivo inexistente.".encode())

            elif data.lower() == "chat":
                # Uma thread recebe mensagens do cliente continuamente
                # enquanto o servidor pode enviar mensagens simultaneamente.
                conn.send("Conectado ao chat. Digite 'sair' para encerrar.".encode())

                def receber_mensagens():
                    while True:
                        try:
                            msg = conn.recv(1024).decode()
                            if msg.lower() == "sair":
                                print(f"Cliente {addr} encerrou o chat.")
                                break
                            print(f"Cliente {addr} diz: {msg}")
                        except:
                            break

                thread_receber = threading.Thread(target=receber_mensagens)
                thread_receber.start()

                while True:
                    try:
                        mensagem = input("")
                        conn.send(mensagem.encode())
                        if mensagem.lower() == "sair":
                            print(f"Chat com cliente {addr} encerrado.")
                            break
                    except:
                        break

            else:
                conn.send("Comando inválido.".encode())
        except Exception as e:
            print(f"Erro com o cliente {addr}: {e}")
            break

    conn.close()


def start_server():
    """Inicia o servidor TCP."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Servidor rodando em {HOST}:{PORT}...")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"Threads ativas: {threading.active_count() - 1}")


if __name__ == "__main__":
    start_server()
