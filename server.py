import socket
import selectors
import sys
import json
import random

from datetime import datetime

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
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] Client {action} at {addr}. Total players: {len(clients)}")

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
        print(f"Error decoding message: {message}")


def handle_name(conn, name):
    addr = conn.getpeername()
    clients[addr] = {"name": name, "score": 0}
    client_answers[addr] = False
    client_states[addr] = "active"
    print(f"Set name for {addr} to {name}")

    confirmation_message = json.dumps(
        {"type": "confirm", "data": {"message": f"Welcome, {name}!"}}
    )
    send_message(conn, confirmation_message)

    # Start the game only if it hasn’t already started
    if not game_started:
        start_game()
    else:
        # Inform new player to wait if the game is ongoing
        waiting_message = json.dumps(
            {"type": "wait", "data": {"message": "Please wait for the next question."}}
        )
        send_message(conn, waiting_message)
        print(f"{name} has to wait for the next question")



def handle_client_disconnect(conn):
    addr = conn.getpeername()

    if addr in clients:

        if client_states.get(addr) == "playing":
            print(f"{clients[addr]['name']} has disconnected.")

            del client_answers[addr]
            del client_states[addr]
            del clients[addr]

            if not any(state == "playing" for state in client_states.values()):
                print("No active players, shutting down...")
                sys.exit(0)
        else:

            print(f"Inactive client {addr} disconnected.")
            del client_states[addr]
            del clients[addr]

    sel.unregister(conn)
    conn.close()

    if addr in client_answers:
        del client_answers[addr]


def start_game():
    global game_started, question_index, game_questions
    game_started = True
    question_index = 0
    game_questions = random.sample(questions, 10)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] Game started with {len(clients)} players.")
    print("Game questions and answers for this session:")
    for idx, q in enumerate(game_questions):
        print(f"Q{idx+1}: {q['question']} | Answer: {q['answer']}")
    send_next_question()

def send_final_scoreboard_and_thank_you():
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] Game over. Final scoreboard sent.")
    send_scoreboard()
    # (Rest of the code)



def send_next_question():
    global question_index
    print(f"send_next_question called: current index = {question_index}")

    if question_index < len(game_questions):
        question = game_questions[question_index]
        label = f"Question {question_index + 1}"
        
        # Log the question details for debugging
        print(f"Sending {label}: {question['question']}")
        print(f"Choices: {question['choices']}")
        print(f"Correct Answer: {question['answer']}")

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
                print(f"{clients[addr]['name']} is now playing")

        for conn in sel.get_map().values():
            if conn.data == read_message:
                addr = conn.fileobj.getpeername()
                if addr in clients and client_states[addr] == "playing":
                    name = clients[addr]["name"]
                    print(f"Sending {label} to {name} {addr}")
                    send_message(conn.fileobj, question_message)

        question_index += 1
    else:
        print("All questions asked, game over.")
        send_final_scoreboard_and_thank_you()



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

    print("Game over. Thank you message sent to all players.")


def handle_answer(conn, answer):
    global question_index
    addr = conn.getpeername()

    if question_index > 0:
        # Fetch the correct answer index for the current question
        correct_answer_index = game_questions[question_index - 1]["answer"]
        
        # Debugging output to log both answers and question details
        print(f"Received answer from {clients[addr]['name']}: {answer}")
        print(f"Expected answer index for '{game_questions[question_index - 1]['question']}': {correct_answer_index}")

        # Compare the received answer index to the correct answer index
        if answer.strip() == correct_answer_index:
            print(f"{clients[addr]['name']} answered correctly!")
            clients[addr]["score"] += 1
        else:
            print(f"{clients[addr]['name']} answered incorrectly.")

        client_answers[addr] = True

        if all(
            client_answers[addr]
            for addr in client_answers
            if client_states[addr] == "playing"
        ):
            send_scoreboard()
            question_index += 1
            send_next_question()
    else:
        print("Question index is not properly set, waiting for the first question.")




def send_scoreboard():
    scoreboard = {clients[addr]["name"]: clients[addr]["score"] for addr in clients}
    scoreboard_message = json.dumps({"type": "scoreboard", "data": scoreboard})
    for conn in sel.get_map().values():
        if conn.data == read_message:  # Only send to active clients
            addr = conn.fileobj.getpeername()
            if addr in clients:  # Check if the client has set their name
                send_message(conn.fileobj, scoreboard_message)


def start_server(host, port):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((host, int(port)))
    server_sock.listen()
    print(f"Server started on {host}:{port}")
    server_sock.setblocking(False)
    sel.register(server_sock, selectors.EVENT_READ, accept_connection)

    while True:
        events = sel.select()
        for key, _ in events:
            callback = key.data
            callback(key.fileobj)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 server.py <IP> <Port>")
        sys.exit(1)

    host = sys.argv[1]
    port = sys.argv[2]
    start_server(host, port)
