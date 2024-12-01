import logging
import socket
import selectors
import sys
import json
import random
import argparse
from datetime import datetime

log_file = "server.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger()

sel = selectors.DefaultSelector()
clients = {}
client_answers = {}
client_states = {}
game_questions = []

questions = [
     {
        "question": "What is the capital of France?",
        "choices": ["Paris", "Rome", "Madrid", "Berlin"],
        "answer": "1"
    },
    {
        "question": "What is 2 + 2?",
        "choices": ["3", "4", "5", "6"],
        "answer": "2"
    },
    {
        "question": "Who wrote 'Hamlet'?",
        "choices": ["Shakespeare", "Tolkien", "Rowling", "Austen"],
        "answer": "1"
    },
    {
        "question": "What is the largest planet in our solar system?",
        "choices": ["Jupiter", "Saturn", "Earth", "Mars"],
        "answer": "1"
    },
    {
        "question": "How many heads are in the tricep?",
        "choices": ["Four", "Two", "Three", "None"],
        "answer": "3"
    },
    {
        "question": "Who gave Luffy the straw hat?",
        "choices": ["Zoro", "His dad", "Garp", "Shanks"],
        "answer": "4"
    },
    {
        "question": "Who is the first boss players will find in Elden Ring after leaving the cave?",
        "choices": ["Morgot", "Tree Sentinal", "Knight Man", "Agheel"],
        "answer": "2"
    },
    {
        "question": "Who won Mr. Olympia Classic Physique in 2024?",
        "choices": ["Cbum", "Urs", "Sam Sulek", "Jeff Nippard"],
        "answer": "1"
    },
    {
        "question": "How tall is Mount Everest",
        "choices": ["Quite", "Not at all", "Kinda", "Mount what?"],
        "answer": "1"
    },
    {
        "question": "Who is the most meta in Mario Kart Wii",
        "choices": ["Dry Bones Bullet Bike", "Mario Standard Kart", "Funky Kong Flame Runner", "Luigi Mach Bike"],
        "answer": "3"
    },
    {
        "question": "What artist almost bought my friend's childhood home in Foco?",
        "choices": ["Train", "21 Savage", "Aesop Rock", "Sting"],
        "answer": "1"
    }
]

question_index = 0
game_started = False

def log_connection_status(action, addr):
    logger.info(f"Client {action} at {addr}. Total players: {len(clients)}")

def send_message(conn, message):
    """Send a message to the client with a newline delimiter."""
    conn.send((message + "\n").encode())

def accept_connection(sock):
    conn, addr = sock.accept()
    log_connection_status("connected", addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read_message)

    welcome_message = json.dumps(
        {"type": "welcome", "data": {"message": "Welcome! Please enter your name:"}}
    )
    send_message(conn, welcome_message)

def read_message(conn):
    try:
        data = conn.recv(1024)
        if data:
            messages = data.decode().split("\n")
            for message in messages:
                if message:
                    handle_message(conn, message)
        else:
            handle_client_disconnect(conn)
    except ConnectionError:
        handle_client_disconnect(conn)

def handle_message(conn, message):
    try:
        message_data = json.loads(message)
        message_type = message_data["type"]

        if message_type == "nameset":
            handle_name(conn, message_data["data"]["name"])
            if not game_started:
                start_game()
        elif message_type == "answer":
            handle_answer(conn, message_data["data"]["answer"])
    except json.JSONDecodeError:
        logger.error(f"Error decoding message: {message}")

def handle_name(conn, name):
    addr = conn.getpeername()
    clients[addr] = {"name": name, "score": 0}
    client_answers[addr] = False
    client_states[addr] = "active"
    logger.info(f"Set name for {addr} to {name}")

    confirmation_message = json.dumps(
        {"type": "confirm", "data": {"message": f"Welcome, {name}!"}}
    )
    send_message(conn, confirmation_message)

    if not game_started:
        start_game()
    else:
        waiting_message = json.dumps(
            {"type": "wait", "data": {"message": "Please wait for the next question."}}
        )
        send_message(conn, waiting_message)
        logger.info(f"{name} has to wait for the next question")

def broadcast_message(message):
    """Send a message to all connected clients."""
    for conn in sel.get_map().values():
        if conn.data == read_message:
            addr = conn.fileobj.getpeername()
            if addr in clients:
                try:
                    send_message(conn.fileobj, message)
                except ConnectionError:
                    logger.error(f"Failed to send message to client {addr}")


def handle_client_disconnect(conn):
    addr = conn.getpeername()
    if addr in clients:
        client_name = clients[addr]["name"]
        logger.info(f"{client_name} has disconnected.")

        # Notify remaining clients about the disconnection
        disconnect_message = json.dumps(
            {"type": "client_disconnect", "data": {"message": f"{client_name} has disconnected."}}
        )
        broadcast_message(disconnect_message)

        # Remove client data
        del client_answers[addr]
        del client_states[addr]
        del clients[addr]

        # If no active players remain, shut down the server
        if not any(state == "playing" for state in client_states.values()):
            logger.info("No active players, shutting down...")
            sys.exit(0)
    else:
        logger.info(f"Inactive client {addr} disconnected.")

    sel.unregister(conn)
    conn.close()

    if addr in client_answers:
        del client_answers[addr]


def start_game():
    global game_started, question_index, game_questions
    game_started = True
    question_index = 0
    game_questions = random.sample(questions, 10)
    logger.info(f"Game started with {len(clients)} players.")
    logger.info("Game questions and answers for this session:")
    for idx, q in enumerate(game_questions):
        logger.info(f"Q{idx+1}: {q['question']} | Answer: {q['answer']}")
    send_next_question()

def send_next_question():
    global question_index
    if question_index < len(game_questions):
        question = game_questions[question_index]
        label = f"Question {question_index + 1}"

        logger.info(f"Sending {label}: {question['question']}")
        logger.info(f"Choices: {question['choices']}")
        logger.info(f"Correct Answer: {question['answer']}")

        question_message = json.dumps(
            {
                "type": "question",
                "data": {
                    "label": label,
                    "question": question["question"],
                    "choices": question["choices"],
                },
            }
        )

        for addr in clients:
            if client_states[addr] == "playing":
                client_answers[addr] = False

        for addr in client_states:
            if client_states[addr] == "active":
                client_states[addr] = "playing"
                logger.info(f"{clients[addr]['name']} is now playing")

        for conn in sel.get_map().values():
            if conn.data == read_message:
                addr = conn.fileobj.getpeername()
                if addr in clients and client_states[addr] == "playing":
                    name = clients[addr]["name"]
                    logger.info(f"Sending {label} to {name} {addr}")
                    send_message(conn.fileobj, question_message)

        question_index += 1
    else:
        logger.info("All questions asked, determining winner.")
        determine_winner()

def determine_winner():
    max_score = max(client["score"] for client in clients.values())
    winners = [client["name"] for client in clients.values() if client["score"] == max_score]

    if len(winners) == 1:
        winner_message = f"{winners[0]} won the game with {max_score} points!"
    else:
        winner_message = f"{' and '.join(winners)} tied the game with {max_score} points!"

    logger.info(winner_message)

    winner_announcement = json.dumps(
        {"type": "winner", "data": {"message": winner_message}}
    )
    for conn in sel.get_map().values():
        if conn.data == read_message:
            send_message(conn.fileobj, winner_announcement)

    reset_game()


def reset_game():
    global clients, client_answers, client_states

    reset_prompt = json.dumps(
        {"type": "reset_prompt", "data": {"message": "Do you want to play again? (yes/no)"}}
    )
    logger.info("Prompting clients to reset the game.")

    # Send reset prompt to all clients
    for conn in sel.get_map().values():
        if conn.data == read_message:
            send_message(conn.fileobj, reset_prompt)

    responses = {}
    disconnect_queue = []  # Track clients who chose "no"

    # Collect responses from all clients
    while len(responses) < len(clients):
        events = sel.select()
        for key, _ in events:
            conn = key.fileobj
            addr = conn.getpeername()
            if addr not in responses:
                try:
                    data = conn.recv(1024).decode().strip()
                    if data.lower() == "yes":
                        responses[addr] = "yes"
                        logger.info(f"{clients[addr]['name']} chose to continue.")
                    elif data.lower() == "no":
                        responses[addr] = "no"
                        logger.info(f"{clients[addr]['name']} chose not to continue.")
                        send_message(conn, json.dumps({"type": "thank_you", "data": {"message": "Thank you for playing!"}}))
                        disconnect_queue.append(conn)  # Queue for disconnection after responses are processed
                except ConnectionError:
                    handle_client_disconnect(conn)
                    responses[addr] = "no"

    # Disconnect clients who chose "no" after all responses are collected
    for conn in disconnect_queue:
        handle_client_disconnect(conn)

    # Filter out disconnected clients
    clients = {addr: info for addr, info in clients.items() if responses.get(addr) == "yes"}
    client_answers = {addr: False for addr in clients}
    client_states = {addr: "active" for addr in clients}

    # Determine if there are players left to restart
    if clients:
        logger.info("Restarting the game with remaining clients.")
        start_game()
    else:
        logger.info("No clients want to continue. Shutting down.")
        send_final_scoreboard_and_thank_you()
        sys.exit(0)






def send_final_scoreboard_and_thank_you():
    send_scoreboard()

    thank_you_message = json.dumps(
        {
            "type": "thank_you",
            "data": {"message": "Thank you for playing the quiz game!"},
        }
    )

    for conn in sel.get_map().values():
        if conn.data == read_message:
            send_message(conn.fileobj, thank_you_message)

    logger.info("Game over. Thank you message sent to all players.")

def handle_answer(conn, answer):
    global question_index
    addr = conn.getpeername()

    if question_index > 0:
        correct_answer_index = game_questions[question_index - 1]["answer"]
        logger.info(f"Received answer from {clients[addr]['name']}: {answer}")
        logger.info(f"Expected answer index: {correct_answer_index}")

        if answer.strip() == correct_answer_index:
            logger.info(f"{clients[addr]['name']} answered correctly!")
            clients[addr]["score"] += 1
        else:
            logger.info(f"{clients[addr]['name']} answered incorrectly.")

        client_answers[addr] = True

        if all(
            client_answers[addr]
            for addr in client_answers
            if client_states[addr] == "playing"
        ):
            send_scoreboard()
            send_next_question()
    else:
        logger.warning("Question index is not properly set, waiting for the first question.")

def send_scoreboard():
    scoreboard = {clients[addr]["name"]: clients[addr]["score"] for addr in clients}
    scoreboard_message = json.dumps({"type": "scoreboard", "data": scoreboard})
    for conn in sel.get_map().values():
        if conn.data == read_message:
            addr = conn.fileobj.getpeername()
            if addr in clients:
                send_message(conn.fileobj, scoreboard_message)

def start_server(host, port):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((host, int(port)))
    server_sock.listen()
    logger.info(f"Server started on {host}:{port}")
    server_sock.setblocking(False)
    sel.register(server_sock, selectors.EVENT_READ, accept_connection)

    while True:
        events = sel.select()
        for key, _ in events:
            callback = key.data
            callback(key.fileobj)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the server.")
    parser.add_argument("-p", "--port", type=int, required=True, help="Port to bind the server.")
    args = parser.parse_args()

    host = "0.0.0.0"
    port = args.port
    start_server(host, port)
