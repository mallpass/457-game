# 457 Game Project

For my project I will be making a simple quiz show game using TCP sockets and python. Hoping to be able to add plenty of features and learn about networks.

**How to play:**
1. **Start the server:** Run the `server.py` script with `python3 server.py -p <Port Number>`
2. **Connect clients:** Run the `client.py` script with `python3 client.py -i <IP address> -p <Port Number>`
3. **Enter Player/Client Names:** Once the connected to the server, players will be prompted to enter thier names.
4. **Game Start:** Once one player has entered their name 10 questions will be randomly selected from the question bank for play.
5. **Mid-game connection:** If a player joins mid-game, they will be prompted to enter their name as normal and be asked to wait until the next question is asked.
6. **Answer Selection:** Players will be asked multiple choice questions. To answer enter in the full text of the choice you think is correct. Every player's score will be broadcast to all connected clients at the end of every turn.
7. **End Game:** After the last question is asked and answered the scoreboard wil be displayed and a winner will be declared. 
8. **Game Reset:** After the winner is declared all players are asked if they'd like to play again. Type yes or no in response. Scores will carry over and if a player chooses not to continue they will be disconnected from the server.

**Roadmap**
If I were to continue working on this project the next step would be to implement an error free gui. I tried working with PyQT5 for the first time to get the extra credit and I got a semi-functional script made (details for how to run 
are provided below, I apologize for any potential confusion over leaving the gui script in the repo, but I figured it would not hurt to leave in). After ironing out the gui the next step would be to implement some security measures, more info 
on the security risks of my script and the improvements I would make are also provided below. I am pretty satisfied with the core functionallity of the project, especially how it relates to networking.

**Retrospective**
Something I really loved about the class and the project were how the homework assignments were related to the project. It was very nice being able to go through the homework assignments and get a feel for the bigger picture with some guidence
then be able to apply what I learned in an open ended project like this. I am really satisfied with the messaging functionality, how the server handles multiple clients and synchronization, and the quality/readability of the code I wrote. 

Aside from the gui and security (or lack thereof), somethings that I think I could improve include: more questions and a better way to store the questions (maybe a separate file rather than in the script itself), making the game more fair
to those who join late, and more timely notifications to players about errors and disconnects. 
 

**GUI Update**
 
I am satisfied with the functionality and error checking of the base client script (client.py) so in my attempts to get a gui working I chose to make a serparate client script (clientui.py).
If you would like to try it I've listed the instructions below. When I test it, the gui seems to run just fine, but please note that there may 
be errors that occur due to my lack of knowledge/understanding/testing.


**How to play with the GUI**
1. **Start the server:** Run the `server.py` script with `python3 server.py -p <Port Number>`
2. **Connect clients:** Run the `clientui.py` script with `python3 clientui.py -i <IP address> -p <Port Number>`
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


**Potential Security Issues**
The scripts both lack any kind of security measures. Neither the server nor client perform any kind of authentication; this issue by itself is not of incredibly high priority since the server doesn't store any important data. However, someone
could take advantage of this lack of authentication as well as the lack of rate limiting to overwhelm the server. The server does not limit the amount of clients that could connect nor does it limit the amount of messages or length of these messages
that can be sent by the client (making it particularly vulnerable to bufferover flow attacks) The communication between the server and client is also very vulnerable. Communication is done in plaintext making it vulnerable to being evesdropped on,
and the server log file is unencrypted. Communication also lacks any input validation so someone smarter than me could probably find a message to send that may cause unexpected behavior in the server. Input validation and adding resource limits could
solve some of these problems, using tls for communication would also help as well as encrypting the server log file. The GUI script solves some of these problems, removing most instances where the client is typing in favor of a button, however the same
vulnerabilites exist here as in the base client script. 
