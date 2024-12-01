import socket
import sys
import json
import argparse

buffer = ""


def handle_message(client_sock, message):
    try:
        msg = json.loads(message)
        message_type = msg.get("type")

        if message_type == "welcome":
            print("Server:", msg["data"]["message"])
            name = input("Enter your name: ")
            send_name(client_sock, name)
        elif message_type == "confirm":
            print("Server:", msg["data"]["message"])
        elif message_type == "question":
            print(f"{msg['data']['label']}: {msg['data']['question']}")
            for idx, choice in enumerate(msg["data"]["choices"]):
                print(f"{idx + 1}. {choice}")
            answer = input("Your answer: ")
            send_answer(client_sock, answer)
        elif message_type == "scoreboard":
            print("Scoreboard:")
            for player, score in msg["data"].items():
                print(f"{player}: {score} points")
        elif message_type == "thank_you":
            print("Server:", msg["data"]["message"])
        elif message_type == "wait":
            print("Server:", msg["data"]["message"])
        elif message_type == "winner":
            print("Server:", msg["data"]["message"])
        elif message_type == "reset_prompt":
            print("Server:", msg["data"]["message"])
            response = input("Your choice (yes/no): ").strip()
            client_sock.send((response + "\n").encode())
        elif message_type == "client_disconnect":
            print("Server:", msg["data"]["message"]) 
        else:
            print("Unknown message type:", message_type)
    except json.JSONDecodeError:
        print("Error decoding message:", message)


def send_name(client_sock, name):
    name_message = json.dumps({"type": "nameset", "data": {"name": name}})
    client_sock.send((name_message + "\n").encode())


def send_answer(client_sock, answer):
    answer_message = json.dumps({"type": "answer", "data": import socket
import sys
import json
import argparse

buffer = ""


def handle_message(client_sock, message):
    try:
        msg = json.loads(message)
        message_type = msg.get("type")

        if message_type == "welcome":
            print("Server:", msg["data"]["message"])
            name = input("Enter your name: ")
            send_name(client_sock, name)
        elif message_type == "confirm":
            print("Server:", msg["data"]["message"])
        elif message_type == "question":
            print(f"{msg['data']['label']}: {msg['data']['question']}")
            for idx, choice in enumerate(msg["data"]["choices"]):
                print(f"{idx + 1}. {choice}")
            answer = input("Your answer: ")
            send_answer(client_sock, answer)
        elif message_type == "scoreboard":
            print("Scoreboard:")
            for player, score in msg["data"].items():
                print(f"{player}: {score} points")
        elif message_type == "thank_you":
            print("Server:", msg["data"]["message"])
        elif message_type == "wait":
            print("Server:", msg["data"]["message"])
        elif message_type == "winner":
            print("Server:", msg["data"]["message"])
        elif message_type == "reset_prompt":
            print("Server:", msg["data"]["message"])
            response = input("Your choice (yes/no): ").strip()
            client_sock.send((response + "\n").encode())
        elif message_type == "client_disconnect":
            print("Server:", msg["data"]["message"]) 
        else:
            print("Unknown message type:", message_type)
    except json.JSONDecodeError:
        print("Error decoding message:", message)


def send_name(client_sock, name):
    name_message = json.dumps({"type": "nameset", "data": {"name": name}})
    client_sock.send((name_message + "\n").encode())


def send_answer(client_sock, answer):
    answer_message = json.dumps({"type": "answer", "data": {"answer": answer}})
    client_sock.send((answer_message + "\n").encode())


def receive_messages(client_sock):
    global buffer
    try:
        data = client_sock.recv(1024).decode()
        if not data:
            raise ConnectionError("Server has disconnected.")
        buffer += data
        messages = buffer.split("\n")

        for message in messages[:-1]:
            handle_message(client_sock, message)

        buffer = messages[-1]
    except (ConnectionError, OSError):
        print("Lost connection to the server. Exiting...")
        sys.exit(1)


def start_client(host, port):
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_sock.connect((host, int(port)))
        print(f"Connected to server at {host}:{port}")

        while True:
            receive_messages(client_sock)

    except ConnectionError:
        print("Unable to connect to the server. Exiting...")
    except KeyboardInterrupt:
        print("Closing connection")
    finally:
        client_sock.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the client.")
    parser.add_argument("-i", "--ip", required=True, help="Server IP or DNS to connect to.")
    parser.add_argument("-p", "--port", type=int, required=True, help="Server port to connect to.")
    args = parser.parse_args()

    host = args.ip
    port = args.port
    start_client(host, port)
{"answer": answer}})
    client_sock.send((answer_message + "\n").encode())


def receive_messages(client_sock):
    global buffer
    try:
        data = client_sock.recv(1024).decode()
        if not data:
            raise ConnectionError("Server has disconnected.")
        buffer += data
        messages = buffer.split("\n")

        for message in messages[:-1]:
            handle_message(client_sock, message)

        buffer = messages[-1]
    except (ConnectionError, OSError):
        print("Lost connection to the server. Exiting...")
        sys.exit(1)


def start_client(host, port):
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_sock.connect((host, int(port)))
        print(f"Connected to server at {host}:{port}")

        while True:
            receive_messages(client_sock)

    except ConnectionError:
        print("Unable to connect to the server. Exiting...")
    except KeyboardInterrupt:
        print("Closing connection")
    finally:
        client_sock.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the client.")
    parser.add_argument("-i", "--ip", required=True, help="Server IP or DNS to connect to.")
    parser.add_argument("-p", "--port", type=int, required=True, help="Server port to connect to.")
    args = parser.parse_args()

    host = args.ip
    port = args.port
    start_client(host, port)
