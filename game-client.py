import socket
import sys

def start_client(ip, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip, port))
    print(f"Connected to server at {ip}:{port}")

    while True:
        try:
            # Wait to receive messages from the server
            data = client.recv(1024)

            # If no data is received, it means the server closed the connection
            if not data:
                print("Connection closed by the server.")
                break

            # Split the received data by newlines to handle multiple messages
            messages = data.decode().split('\n')
            for message in messages:
                if message:
                    print(f"Server: {message}")

                    # If the server asks for the player's name, allow input
                    if "Please enter your name:" in message:
                        name = input("Enter your name: ")
                        client.send(name.encode())

        except ConnectionResetError:
            print("Connection was reset by the server.")
            break

    client.close()  # Close the client socket when done

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 game-client.py <IP> <Port>")
        sys.exit(1)

    ip = sys.argv[1]
    port = int(sys.argv[2])

    start_client(ip, port)
