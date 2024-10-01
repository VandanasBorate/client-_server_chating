
import socket
import threading

clients = {}  # Dictionary to store client addresses, sockets, and usernames

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 12345))  # Bind to all interfaces on port 12345
    server.listen(5)
    print("Server is connected and listening for clients...\n")

    while True:
        client_socket, addr = server.accept()

        # Receive the username from the client
        username = client_socket.recv(1024).decode('utf-8').strip()
        clients[addr] = {'socket': client_socket, 'username': username}
        print(f"New connection from {addr} with username {username}")
        
        # Send welcome message and connected client list to the new client
        welcome_message = f"Warm Welcome to the server, {username}! You are now connected.\n"
        client_socket.send(welcome_message.encode('utf-8'))
        
        # Send updated list of connected clients to all clients
        send_connected_clients()

        threading.Thread(target=handle_client, args=(client_socket, addr)).start()

def handle_client(client_socket, addr):
    try:
        username = clients[addr]['username']  # Get the username associated with this client
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                if message.lower() == 'exit':
                    print(f"Client {username} ({addr}) requested to disconnect.")
                    break
                elif message.startswith('@'):
                    handle_private_message(message, addr)
                else:
                    broadcast_message(f" Message Received From {username} ({addr[0]}): {message}", client_socket)

            else:
                print(f"Client {username} ({addr}) disconnected.")
                break
    finally:
        if addr in clients:
            del clients[addr]
            print(f"Client {username} ({addr}) has been removed from the client list.")
            send_connected_clients()
        client_socket.close()

def handle_private_message(message, sender_addr):
    try:
        recipient_ip, private_message = message[1:].split(' ', 1)
        recipient_addr = None
        sender_username = clients[sender_addr]['username']
        for addr in clients.items():
            if addr[0] == recipient_ip:
                recipient_addr = addr
                break
        if recipient_addr:
            recipient_socket = clients[recipient_addr]['socket']
            recipient_socket.send(f"Private message from {sender_username} ({sender_addr[0]}): {private_message}".encode('utf-8'))
        else:
            clients[sender_addr]['socket'].send("Recipient not found.".encode('utf-8'))
    except Exception as e:
        print(f"Failed to send private message.")

def broadcast_message(message, sender_socket=None):
    for client_info in clients.values():
        client_socket = client_info['socket']
        if client_socket != sender_socket:
            try:
                client_socket.send(message.encode('utf-8'))
            except Exception as e:
                print(f"Failed to send message: {e}")
                client_socket.close()

def send_connected_clients():
    client_list = "Connected clients:\n"
    for addr, client_info in clients.items():
        client_list += f"Client {client_info['username']} ({addr[0]}:{addr[1]})\n"
    
    for client_info in clients.values():
        client_socket = client_info['socket']
        try:
            client_socket.send(client_list.encode('utf-8'))
        except Exception as e:
            print(f"Failed to send connected clients list.")
            client_socket.close()

if __name__ == "__main__":
    start_server()

