import socket
import sys
import json
import threading
import argparse
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QLineEdit, QInputDialog
)
from PyQt5.QtCore import pyqtSignal


class QuizClient(QWidget):
    update_terminal_signal = pyqtSignal(str)
    update_question_signal = pyqtSignal(str, list)
    update_scoreboard_signal = pyqtSignal(dict)
    restart_game_signal = pyqtSignal()

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buffer = ""

        self.init_ui()
        self.connect_to_server()

        self.update_terminal_signal.connect(self.append_to_terminal)
        self.update_question_signal.connect(self.update_question)
        self.update_scoreboard_signal.connect(self.update_scoreboard)
        self.restart_game_signal.connect(self.show_restart_prompt)

        self.running = True
        self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.receive_thread.start()

    def init_ui(self):
        self.setWindowTitle("Quiz Game Client")
        layout = QVBoxLayout()

        self.question_label = QLabel("Waiting for question...", self)
        self.question_label.setWordWrap(True)
        layout.addWidget(self.question_label)

        self.answer_buttons = []
        button_layout = QHBoxLayout()
        for i in range(4):
            btn = QPushButton(f"Choice {i + 1}", self)
            btn.clicked.connect(lambda checked, i=i: self.send_answer(i + 1))
            btn.setEnabled(False) 
            button_layout.addWidget(btn)
            self.answer_buttons.append(btn)
        layout.addLayout(button_layout)

        self.scoreboard_label = QLabel("Scoreboard:", self)
        layout.addWidget(self.scoreboard_label)
        self.scoreboard_text = QTextEdit(self)
        self.scoreboard_text.setReadOnly(True)
        layout.addWidget(self.scoreboard_text)

        self.terminal_label = QLabel("Server Messages:", self)
        layout.addWidget(self.terminal_label)
        self.terminal_text = QTextEdit(self)
        self.terminal_text.setReadOnly(True)
        layout.addWidget(self.terminal_text)

        self.restart_label = QLabel("", self)
        self.restart_label.hide()
        layout.addWidget(self.restart_label)

        self.restart_buttons = QHBoxLayout()
        self.yes_button = QPushButton("Yes", self)
        self.no_button = QPushButton("No", self)
        self.yes_button.clicked.connect(lambda: self.send_restart_response("yes"))
        self.no_button.clicked.connect(lambda: self.send_restart_response("no"))
        self.restart_buttons.addWidget(self.yes_button)
        self.restart_buttons.addWidget(self.no_button)
        self.yes_button.hide()
        self.no_button.hide()
        layout.addLayout(self.restart_buttons)

        self.setLayout(layout)

    def connect_to_server(self):
        try:
            self.client_sock.connect((self.host, int(self.port)))
            self.append_to_terminal(f"Connected to server at {self.host}:{self.port}")
        except ConnectionError:
            self.append_to_terminal("Unable to connect to the server. Exiting...")
            sys.exit(1)

    def append_to_terminal(self, message):
        self.terminal_text.append(message)

    def update_question(self, question, choices):
        self.question_label.setText(question)
        for i, choice in enumerate(choices):
            self.answer_buttons[i].setText(choice)
            self.answer_buttons[i].setEnabled(True)

    def disable_buttons(self):
        for btn in self.answer_buttons:
            btn.setEnabled(False)

    def update_scoreboard(self, scores):
        self.scoreboard_text.clear()
        for player, score in scores.items():
            self.scoreboard_text.append(f"{player}: {score} points")

    def send_answer(self, answer):
        answer_message = json.dumps({"type": "answer", "data": {"answer": str(answer)}})
        self.client_sock.send((answer_message + "\n").encode())
        self.disable_buttons()

    def handle_message(self, message):
        try:
            msg = json.loads(message)
            message_type = msg.get("type")

            if message_type == "welcome":
                self.update_terminal_signal.emit(msg["data"]["message"])
                name, ok = QInputDialog.getText(self, "Enter Name", "Please enter your name:")
                if ok and name.strip():
                    name_message = json.dumps({"type": "nameset", "data": {"name": name.strip()}})
                    self.client_sock.send((name_message + "\n").encode())
            elif message_type == "question":
                question = msg["data"]["question"]
                choices = msg["data"]["choices"]
                self.update_question_signal.emit(question, choices)
            elif message_type == "scoreboard":
                self.update_scoreboard_signal.emit(msg["data"])
            elif message_type == "reset_prompt":
                self.restart_game_signal.emit()
            elif message_type in ["thank_you", "wait", "winner", "client_disconnect"]:
                self.update_terminal_signal.emit(msg["data"]["message"])
            else:
                self.update_terminal_signal.emit(f"Unknown message type: {message_type}")
        except json.JSONDecodeError:
            self.update_terminal_signal.emit("Error decoding message from server.")

    def receive_messages(self):
        while self.running:
            try:
                data = self.client_sock.recv(1024).decode()
                if not data:
                    raise ConnectionError("Server has disconnected.")
                self.buffer += data
                messages = self.buffer.split("\n")

                for message in messages[:-1]:
                    self.handle_message(message)

                self.buffer = messages[-1]
            except ConnectionError:
                self.update_terminal_signal.emit("Lost connection to the server. Exiting...")
                self.running = False
                self.client_sock.close()
                break

    def show_restart_prompt(self):
        self.restart_label.setText("Do you want to restart the game?")
        self.restart_label.show()
        self.yes_button.show()
        self.no_button.show()

    def send_restart_response(self, response):
        self.restart_label.hide()
        self.yes_button.hide()
        self.no_button.hide()
        self.append_to_terminal(f"Sending restart response: {response}")
        self.client_sock.send((response + "\n").encode())

    def closeEvent(self, event):
        self.running = False
        self.client_sock.close()
        event.accept()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the client.")
    parser.add_argument("-i", "--ip", required=True, help="Server IP or DNS to connect to.")
    parser.add_argument("-p", "--port", type=int, required=True, help="Server port to connect to.")
    args = parser.parse_args()

    host = args.ip
    port = args.port

    app = QApplication(sys.argv)
    client = QuizClient(host, port)
    client.show()
    sys.exit(app.exec_())
