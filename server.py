import socket
import threading

# Dictionary to store client connections based on IP
clients = {}

# Function to handle communication with each client
def handle_client(client_socket, client_address):
    # Register client by a unique ID (in this case, using client IP)
    client_ip = client_address[0]
    clients[client_ip] = client_socket
    print(f"Client {client_ip} connected.")

    try:
        while True:
            # Receive the message from the client
            message = client_socket.recv(1024)
            if not message:
                break  # Disconnect if no message is received

            # Decode the message and assume format: "recipient_ip:message"
            message = message.decode('utf-8')
            print(f"Received from {client_ip}: {message}")

            # Parse the message to extract recipient IP and content
            try:
                recipient_ip, content = message.split(":", 1)
            except ValueError:
                print("Invalid message format. Skipping...")
                continue

            # Include the sender's IP address in the message
            sender_ip = client_ip  # Sender's IP address
            message_to_send = f"From {sender_ip}: {content}"

            # Forward the message to the recipient (recipient's IP address)
            if recipient_ip in clients:
                print(f"Forwarding message to {recipient_ip}.")
                clients[recipient_ip].send(message_to_send.encode('utf-8'))
            else:
                print(f"Client {recipient_ip} not found. Message not forwarded.")
                client_socket.send("Recipient not found.".encode('utf-8'))
    finally:
        # Clean up when the client disconnects
        del clients[client_ip]
        client_socket.close()
        print(f"Client {client_ip} disconnected.")

# Main function to start the server
def start_server(host='10.10.217.196', port=5001):
    # Create a socket to listen for incoming connections
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)  # Maximum number of queued connections

    print(f"Server started on {host}:{port}")

    try:
        while True:
            # Wait for incoming client connections
            client_socket, client_address = server_socket.accept()
            print(f"New connection from {client_address}")

            # Create a new thread for each client
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()
    except KeyboardInterrupt:
        print("Server stopped.")

if __name__ == "__main__":
    start_server()
