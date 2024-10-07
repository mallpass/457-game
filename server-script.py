def collect_names(clients):
    player_names = {}
    for addr, client_socket in clients.items():
        client_socket.send("Please enter your name:".encode())
        name = client_socket.recv(1024).decode()
        player_names[addr] = name
        client_socket.send(f"Welcome: {name}\nWaiting on other players...".encode())
    return player_names
