import socket
import hashlib
import threading

# Configurações do cliente
SERVER_HOST = "127.0.0.1"  # Endereço do servidor
SERVER_PORT = 12345  # Porta do servidor


def verificar_hash(filepath, esperado):
    """Verifica se o hash do arquivo recebido é igual ao esperado."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest() == esperado


def start_client():
    """Inicia o cliente TCP."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_HOST, SERVER_PORT))
    print("Conectado ao servidor!")

    while True:
        comando = input("Digite um comando (Sair, Arquivo <nome>, Chat): ")
        client.send(comando.encode())

        if comando.lower() == "sair":
            print("Desconectando...")
            break

        elif comando.startswith("Arquivo"):
            # Recebe cabeçalho do arquivo
            header = client.recv(1024).decode()
            if header.startswith("Erro"):
                print(header)  # Mensagem de erro
            else:
                filename, filesize, filehash, status = header.split("|")
                filesize = int(filesize)

                # Verifica se a transferência está OK
                if status == "ok":
                    filepath = f"baixado_{filename}"

                    # Recebe os dados do arquivo
                    with open(filepath, "wb") as f:
                        recebido = 0
                        while recebido < filesize:
                            chunk = client.recv(4096)
                            f.write(chunk)
                            recebido += len(chunk)

                    # Verifica o hash
                    if verificar_hash(filepath, filehash):
                        print(
                            f"Arquivo '{filename}' recebido e verificado com sucesso!"
                        )
                    else:
                        print(f"Erro: o hash do arquivo '{filename}' não confere!")
                else:
                    print(f"Erro ao receber o arquivo: {status}")

        elif comando.lower() == "chat":
            # Uma thread recebe mensagens do servidor continuamente
            # enquanto o cliente pode enviar mensagens simultaneamente.
            print("Conectado ao chat. Digite 'sair' para encerrar.")

            def receber_mensagens():
                while True:
                    try:
                        msg = client.recv(1024).decode()
                        if msg.lower() == "sair":
                            print("Servidor encerrou o chat.")
                            break
                        print(f"Servidor: {msg}")
                    except:
                        break

            thread_receber = threading.Thread(target=receber_mensagens)
            thread_receber.start()

            while True:
                try:
                    mensagem = input("")
                    client.send(mensagem.encode())
                    if mensagem.lower() == "sair":
                        print("Chat encerrado.")
                        break
                except:
                    break

    client.close()


if __name__ == "__main__":
    start_client()
