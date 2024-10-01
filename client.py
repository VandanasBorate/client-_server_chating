
import socket
import threading
import os  # Import os to get the username of the local machine


def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    client.connect(('192.168.1.12', 12345))  # Change IP to your server's IP

    # Automatically get the local machine's username
    username = os.getlogin()  
    client.send(username.encode('utf-8'))  # Send the username to the server upon connection

    # Start a thread to receive messages
    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.daemon = True  # Ensure the thread exits when the main program exits
    receive_thread.start()

    # Start sending messages
    send_messages(client)


def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                # Move the cursor to the beginning of the line and clear it
                print(f"\r{' ' * 100}\r", end="")  # Clear the current line
                print(f"\n{message}")  # Display the received message
                print("Enter your message (or @<recipient_ip> <message> for private message): ", end="", flush=True)  # Display the input prompt
            else:
                break
        except:
            break

def send_messages(client_socket):
    while True:
        message = input()  # Remove the prompt here
        client_socket.send(message.encode('utf-8'))
        print("Enter your message (or @<recipient_ip> <message> for private message):", end="", flush=True)  # Print the input prompt after sending a message

if __name__ == "__main__":
    start_client()
