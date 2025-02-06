import socket
import threading
import os

HOST = "127.0.0.1"
PORT = 12345

# Função para lidar com cada cliente
def handle_client(conn, addr):
    print(f"Conexão estabelecida com {addr}")
    try:
        request = conn.recv(1024).decode()
        if not request:
            return
        
        # Pega a primeira linha da requisição (GET /arquivo.html HTTP/1.0)
        request_line = request.split("\n")[0]
        print(f"Requisição recebida: {request_line}")
        
        # Extrai o caminho do arquivo solicitado
        parts = request_line.split()
        if len(parts) < 2:
            return
        filepath = parts[1].lstrip("/")  # Remove a barra inicial
        
        # Define "index.html" como padrão
        if filepath == "":
            filepath = "index.html"
        
        # Verifica se o arquivo existe
        if os.path.exists(filepath) and os.path.isfile(filepath):
            with open(filepath, "rb") as f:
                content = f.read()
            
            # Determina o tipo de conteúdo
            if filepath.endswith(".html"):
                content_type = "text/html"
            elif filepath.endswith(".jpeg") or filepath.endswith(".jpg"):
                content_type = "image/jpeg"
            else:
                content_type = "application/octet-stream"
            
            # Monta a resposta HTTP 200
            response = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: {content_type}\r\n"
                f"Content-Length: {len(content)}\r\n"
                f"Connection: close\r\n\r\n"
            ).encode() + content
        else:
            # Responde com 404 Not Found
            response = (
                "HTTP/1.1 404 Not Found\r\n"
                "Content-Type: text/html\r\n"
                "Connection: close\r\n\r\n"
                "<html><body><h1>404 Not Found</h1></body></html>"
            ).encode()
        
        conn.sendall(response)
    except Exception as e:
        print(f"Erro ao processar requisição de {addr}: {e}")
    finally:
        conn.close()

# Inicia o servidor
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)  # Permite até 5 conexões simultâneas
    print(f"Servidor HTTP rodando em http://{HOST}:{PORT}")
    
    try:
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
    except KeyboardInterrupt:
        print("Servidor encerrado.")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()
