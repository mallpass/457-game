import selectors
import socket
import types
import sys

sel = selectors.DefaultSelector()
clients = {}  # Global dictionary to track connected clients
num_connected = 0  # Global variable to track the number of connected clients
names = {}  # Store player names


def accept_wrapper(sock, num_players):
    global num_connected
    conn, addr = sock.accept()  # Accept the new connection
    print(f"Client {addr} connected.")
    conn.setblocking(False)  # Make the connection non-blocking
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

    num_connected += 1
    clients[addr] = conn

    welcome_message = (f"Connected to server {addr[0]}, {addr[1]}. "
                       f"Players {num_connected}/{num_players} are connected.")
    conn.send(welcome_message.encode())

    # Broadcast the current player count to all clients
    broadcast_message(f"Waiting for required number of players {num_connected}/{num_players}")

    # If the required number of players have connected, broadcast "All players have joined!" and start the game
    if num_connected == num_players:
        print("All players have connected!")
        broadcast_message("All players have joined!")
        # Move into game state and ask for names
        request_player_names()


def request_player_names():
    """Ask all clients to enter their names."""
    broadcast_message("Please enter your name:")
    # Now the server will wait for client responses


def broadcast_message(message):
    message += "\n"  # Add newline as delimiter
    for addr, client_socket in clients.items():
        try:
            client_socket.send(message.encode())
        except Exception as e:
            print(f"Failed to send message to {addr}: {e}")


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Read the data
        if recv_data:
            message = recv_data.decode()
            print(f"Received data: {message} from {data.addr}")
            # If we are waiting for player names
            if data.addr not in names:
                # Store the name and send confirmation back to the client
                names[data.addr] = message.strip()
                confirmation_message = f"Welcome: {names[data.addr]}"
                sock.send(confirmation_message.encode())
            else:
                print(f"Unexpected message from {data.addr}: {message}")
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()
            clients.pop(data.addr, None)  # Remove client on disconnect

    if mask & selectors.EVENT_WRITE and data.outb:
        sent = sock.send(data.outb)
        data.outb = data.outb[sent:]


def start_server(ip, port, num_players):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip, port))
    server.listen()
    print(f"Server listening on {ip}:{port}")
    print(f"Waiting for {num_players} players to connect...")
    server.setblocking(False)
    sel.register(server, selectors.EVENT_READ, data=None)

    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj, num_players)
            else:
                service_connection(key, mask)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 game-server.py <IP> <Port> <num players>")
        sys.exit(1)

    ip = sys.argv[1]
    port = int(sys.argv[2])
    num_players = int(sys.argv[3])

    start_server(ip, port, num_players)
