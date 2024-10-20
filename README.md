# 457 Game Project

For my project I will be making a simple quiz show game using TCP sockets and python. Hoping to be able to add plenty of features and learn about networks.

**How to play:**
1. **Start the server:** Run the `server.py` script with `python3 server.py <IP address> <Port Number>`
2. **Connect clients:** Run the `client.py` script with `python3 client.py <IP address> <Port Number>`
3. **Enter Player/Client Names:** Once the connected to the server, players will be prompted to enter thier names.
4. **Game Start:** Once one player has entered their name 10 questions will be randomly selected from the question bank for play.
5. **Mid-game connection:** If a player joins mid-game, they will be prompted to enter their name as normal and be asked to wait until the next question is asked.
6. **Answer Selection:** Players will be asked multiple choice questions. To answer enter in the full text of the choice you think is correct. Every player's score will be broadcast to all connected clients at the end of every turn.
7. **More to come**

**Technologies used:**
* Python
* Sockets
