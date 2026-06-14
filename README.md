1) Project Description
Keep Talking and LAMPI Doesn’t Explode is a game where players must work together to defuse LAMPIs in time before it explodes by solving puzzles together on the screen. One player, called the Expert, has access to the manual on a website with the defusal instructions while two Puzzle Solvers must solve puzzles on their LAMPIs under a time limit. The trick is that the Experts cannot see the LAMPI screens, and the Puzzle Solvers cannot see the website’s manual, requiring the Puzzle Solvers to communicate facts about LAMPI to the Expert while the Expert must communicate how to solve them. 


Figure 1: Intended layout for how to play Keep Talking and LAMPI Doesn’t Explode

Although our project is the LAMPI-rendition of the actual game called Keep Talking and Nobody Explodes, the two key differences are that the original game is done on one computer to control the game and disarm the bomb and has instructions on another computer. Stretching this part of the game over MQTT turned out to be our most difficult aspect because we have a controller computer with instructions that acts as the host and Single Point of Truth. Additionally, on top of the independent puzzles that only require one Puzzle Solver and the Expert, we attempted puzzles that require collaboration between the two LAMPIs. An example of an independent puzzle is the Wire Cutting Puzzle, where depending on colors and textures of the wires shown, the Puzzle Solver must cut a certain wire according to the Expert’s instructions. An example of a collaborative puzzle is the Slider Puzzle where according to the other Puzzle Solver’s original LED color, you must change the sliders to a certain value. On a technical level, we extend the original LAMPI assignment by redesigning the MQTT topic hierarchy to communicate between the website and the puzzle’s current state to initiate certain screens, timers, etc. through the MQTT broker. The LAMPI interface during gameplay will have on-screen buttons to initiate each puzzle in addition to controlled LED sequences for certain puzzles and “exploding” effects.



2) System Architecture

Figure 2: System Architecture Diagram
3) Project Plan
Our original walking skeleton was that we would demonstrate basic MQTT communication through our new topic hierarchy by having the Expert press START on the Django website, which then publishes an MQTT message, triggering an LED sequence on the LAMPI as an example puzzle. We changed our original milestone list from the midpoint demo when we realized the MQTT setup would prove to be much harder than we anticipated.

Table 1: Original Milestone List after Midpoint Demo
Week
Dates
Milestone
Deliverables
2
Apr 2 - Apr 8
Core Feature 1
Make blank Django website
Configure Mosquitto
Make Kivy bomb interface to select game
Screen with 3-5 buttons
3
Apr 9 - Apr 15
Midpoint Prep
Start writing instructions on games for expert
Add timer to both LAMPIs that coordinate
Make start button on website that initializes game
Make 1 solo game
Make 1 partner game
4
Apr 16
Midpoint Demo (in-class)
1 partner game
1 solo game
Report, video, and presentation is prepared.
4+
Apr 16 - Apr 22
Core Feature 2
Make 3 games
Make Level select on website to initialize different difficulties
5
Apr 23 - Apr 29
Integration & Polish
Make final 5 games
6
Apr 30 - May 7
Final Demo Prep
Bug fix and refine games, lock in
Report, video, slides, and presentation is prepared. We will demonstrate a more complex game-play (more time to defuse the LAMPI, more complex puzzles, puzzles across two LAMPIs, etc.) that builds upon ideas from the midpoint demo.

Due to the difficulty in setting up the MQTT communication between the Django and the LAMPI, we heavily descoped our project by aiming for 1 individual and 1 collaborative puzzle that had a complete sequence from initiating the overall game to the win/loss event. We also weren’t able to complete as many puzzles as we originally planned for since designing the visual assets, writing the puzzle’s game logic, and connecting to the topics resulted in a lot more effort than we anticipated. As a result, we shifted our focus to one full game loop and we were ultimately able to mostly accomplish it with the wire game working, coordinated starting, and a lose state that sends back to the main host site. On the backend, we have the logic for partner puzzles and one more puzzle developed. In total, we spent about 40 hours each on the project so we are pretty proud of the technical side, though the scale is much smaller than we hoped.
4) Process and Methods
When we were building the walking-skeleton, we naturally divided the three core sections of our game among the three of us:
Setting up Django Website through new EC2 Instance - Daniel
Designing MQTT Topic Hierarchy - Norah
Building Kivy UI on a single LAMPI with Puzzle Assets - Zijin
Due to the time constraints, we created multiple prioritization lists as we tackled certain features, but here is our overall prioritization list with asynchronous tasks. The idea was that two people would work on a high-priority task while an individual person could work on an asynchronous task.
Feature Prioritization List
MQTT connection between Django and LAMPI to send and receive basic messages
Completing the entire Wire Cutting Puzzle’s logic
Displaying the instruction manual’s PDF in Django
Making a complete game loop
Completing the entire collaborative puzzle
Asynchronous Tasks List
Design LED sequence for winning and losing the game.
Visual timer on the LAMPI
Making win and lose screens on Django

While tackling certain features, we considered multiple alternatives for how we would handle the timer, where the Single Point of Truth (SPOT) would be, and how much the topic hierarchy should be split due to our time constraints.

The biggest obstacle that we encountered was connecting the Django website to LAMPI through MQTT as the association code wasn’t published to the LAMPI’s screen and the backend logic for that pairing proved difficult. Therefore, we ultimately hard-coded the LAMPI pairings so we could finish other core features. In addition, the collaborative game took a while to set up since the website needed to publish messages to the same topic that both of the LAMPIs were subscribed to, but we ran into many timing issues that we later debugged to make the LAMPIs synchronous.
5) Results
Our finished project contains:
Working LAMPI UI interface. This includes the entire UI from starting the game, connecting with the website, displaying the variety of puzzles, and ending the game with specific loss events.
Working Django website. This includes the ability to start the game from the Expert’s side whenever the two LAMPIs are connected, displaying the manual to the Expert.
Complete game loop. This describes the entire sequence that the players engage in to play and finish the game:
Both LAMPIs are turned on. Both Puzzle Solvers start the game from the LAMPI and are stuck on the “Waiting for Host” screen.
Expert starts the game from the website, transitioning the Expert to the manual and the Puzzle Solvers to the Puzzle Menu screen. 
When the Puzzle Solvers unsuccessfully/successfully solve the puzzles, then a certain ending screen appears on both the website and the LAMPIs.

Compared to the original plan where we intended to entirely complete ~5 puzzles with varying level difficulties, we have one solo puzzle where the solo puzzle is fully fleshed out with random states and a unique solution to each state based on expert instructions. We also have functionality for a coordinated puzzle in the backend, although it’s not synced with the frontend.

6) Conclusions
During this project, the course concepts that were reinforced/extended were MQTT, Django, HTML/CSS/JS, Pigpio, Kivy UI, and game design. We most extensively dove into MQTT. Beyond the original course material, we did a lot of different manipulation of MQTT, this included switching the bridge from each pi to the EC2 instead of from the EC2 to the Pi. This made it so our we had multiple points of truth– some state tracked on each lampi and some state tracked on the ec2. In addition, we did more advanced Web development by making multiple designed screens and a PDF viewer. In addition, we extended the Kivy UI by focusing on screen changes from button presses since the course’s LAMPI didn’t have a structure to control different screens. We implemented different loading conditions in the screen for randomization with this switching. Finally, we implemented a lot of game design elements like developing instructions, different game states, and game coordination through MQTT.

7) References
https://www.bombmanual.com/
When designing the manual to write the instructions on how to solve each puzzle, we referenced the original Keep Talking and Nobody Explodes manual.
