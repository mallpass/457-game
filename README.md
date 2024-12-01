# 457 Game Project

For my project I will be making a simple quiz show game using TCP sockets and python. Hoping to be able to add plenty of features and learn about networks.

**How to play:**
1. **Start the server:** Run the `server.py` script with `python3 server.py <IP address> <Port Number>`
2. **Connect clients:** Run the `client.py` script with `python3 client.py <IP address> <Port Number>`
3. **Enter Player/Client Names:** Once the connected to the server, players will be prompted to enter thier names.
4. **Game Start:** Once one player has entered their name 10 questions will be randomly selected from the question bank for play.
5. **Mid-game connection:** If a player joins mid-game, they will be prompted to enter their name as normal and be asked to wait until the next question is asked.
6. **Answer Selection:** Players will be asked multiple choice questions. To answer enter in the full text of the choice you think is correct. Every player's score will be broadcast to all connected clients at the end of every turn.
7. **End Game:** After the last question is asked and answered the scoreboard wil be displayed and a winner will be declared. 
8. **Game Reset:** After the winner is declared all players are asked if they'd like to play again. Type yes or no in response. Scores will carry over and if a player chooses not to continue they will be disconnected from the server. 
 

**GUI Update**

For the final update I wanted to get a gui working for the game as making gui's is something I do not have any experience with. 
I am satisfied with the functionality and error checking of the base client script so in my attempts to get a gui working I chose to make a serparate client script 
called clientui. If you would like to try it I've listed the instructions below. When I test it, the gui seems to run just fine, but please note that there may 
be errors that occur due to my lack of knowledge/understanding/testing.

**How to play with the GUI**
1. **Start the server:** Run the `server.py` script with `python3 server.py <IP address> <Port Number>`
2. **Connect clients:** Run the `clientui.py` script with `python3 clientui.py <IP address> <Port Number>`
3. **Enter Player/Client Names:** Once the connected to the server, two new windows will launch, the first will prompt players to enter thier names.
4. **Game Start:** Once one player has entered their name 10 questions will be randomly selected from the question bank for play.
5. **Mid-game connection:** If a player joins mid-game, they will be prompted to enter their name as normal and be asked to wait until the next question is asked.
6. **Answer Selection:** Players will be asked multiple choice questions. To answer press the button of the choice you think is correct. The scoreboard in the window will update after every question.
7. **End Game:** After the last question is asked and answered the scoreboard wil be displayed and a winner will be declared. 
8. **Game Reset:** After the winner is declared all players are asked if they'd like to play again. Select yes or no as a response. Scores will carry over and if a player chooses not to continue they will be disconnected from the server. 

**Technologies used:**
* Python
* Sockets
* PyQt5
