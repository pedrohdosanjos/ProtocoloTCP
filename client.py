import socket
import hashlib
import threading

# Configurações do cliente: endereço e porta do servidor.
SERVER_HOST = "127.0.0.1"  # Endereço do servidor (localhost).
SERVER_PORT = 12345  # Porta do servidor.


# Função para verificar o hash do arquivo recebido.
# REQUISITO: Validar integridade do arquivo recebido.
def verificar_hash(filepath, esperado):
    sha256 = hashlib.sha256()  # Inicializa o hash SHA-256.
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):  # Lê o arquivo em chunks.
            sha256.update(chunk)
    return sha256.hexdigest() == esperado  # Compara com o hash esperado.


# Cliente TCP principal.
def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria o socket TCP.
    client.connect((SERVER_HOST, SERVER_PORT))  # Conecta ao servidor.
    print("Conectado ao servidor!")

    while True:
        # Entrada do usuário para enviar comandos ao servidor.
        comando = input("Digite um comando (Sair, Arquivo <nome>, Chat): ")
        client.send(comando.encode())  # Envia o comando.

        if comando.lower() == "sair":  # REQUISITO: Finalizar conexão com "Sair".
            print("Desconectando...")
            break

        elif comando.startswith("Arquivo"):
            # REQUISITO: Receber arquivos e verificar hash.
            header = client.recv(1024).decode()  # Recebe cabeçalho do arquivo.
            if header.startswith("Erro"):
                print(header)  # Mensagem de erro no servidor.
            else:
                # Extrai metadados do cabeçalho.
                filename, filesize, filehash, status = header.split("|")
                filesize = int(filesize)

                if status == "ok":
                    filepath = f"baixado_{filename}"  # Caminho para salvar o arquivo.

                    # Recebe o arquivo em chunks e salva localmente.
                    with open(filepath, "wb") as f:
                        recebido = 0
                        while recebido < filesize:
                            chunk = client.recv(4096)
                            f.write(chunk)
                            recebido += len(chunk)

                    # Verifica o hash do arquivo recebido.
                    if verificar_hash(filepath, filehash):
                        print(
                            f"Arquivo '{filename}' recebido e verificado com sucesso!"
                        )
                    else:
                        print(f"Erro: o hash do arquivo '{filename}' não confere!")
                else:
                    print(f"Erro ao receber o arquivo: {status}")

        elif comando.lower() == "chat":
            # REQUISITO: Implementar o chat.
            print("Conectado ao chat. Digite 'sair' para encerrar.")

            # Função para receber mensagens do servidor.
            def receber_mensagens():
                while True:
                    try:
                        msg = client.recv(1024).decode()  # Recebe mensagem do servidor.
                        if msg.lower() == "sair":  # Servidor encerra o chat.
                            print("Servidor encerrou o chat.")
                            break
                        print(f"Servidor: {msg}")
                    except:
                        break

            # Thread para gerenciar mensagens recebidas do servidor.
            thread_receber = threading.Thread(target=receber_mensagens)
            thread_receber.start()

            # Cliente envia mensagens para o servidor.
            while True:
                try:
                    mensagem = input("")
                    client.send(mensagem.encode())
                    if mensagem.lower() == "sair":  # Cliente encerra o chat.
                        print("Chat encerrado.")
                        break
                except:
                    break

    client.close()  # Fecha o socket ao encerrar.
    print("Cliente desconectado.")


if __name__ == "__main__":
    start_client()
