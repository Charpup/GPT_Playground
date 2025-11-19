# Naruto Chūnin Exam Adventure

This repository contains a simple command‑line game inspired by the **Chūnin Exam arc** of *Naruto*.  The game is built on top of mechanics borrowed from the 2024/5.5 edition of Dungeons & Dragons, including the standard ability score array and heroic inspiration【302656013783284†L88-L152】【109094228942248†L148-L180】.  Players progress through the three exam phases—written test, Forest of Death, and preliminary matches—while making ability checks against DCs using d20 rolls.  An automated Dungeon Master adjudicates events, combats and branching outcomes.

## Features

- **Character creation** using the standard array of ability scores (16, 14, 13, 12, 10, 8)【302656013783284†L88-L152】.
- **Heroic inspiration**, granting each player a single reroll per session【109094228942248†L148-L180】.
- A narrative that mirrors the **written test**, **Forest of Death**, and **preliminary matches** of the Chūnin exams【999661209240364†L269-L417】.
- Automated encounters and ability checks requiring decisions to cheat, fight or endure, reducing the player’s calculation burden.
- Support for **1–3 players**, echoing the three‑nin team structure in Naruto.

## Running the Game

To play, ensure you have Python 3 installed.  Run the script from the command line:

```bash
python3 naruto_game.py
```

Follow the prompts to specify the number of players, enter character names and make choices during each exam phase.  When prompted to spend inspiration, respond with the number corresponding to your choice.

## Extending

This project is intentionally simple to illustrate how one might automate a tabletop RPG story.  For a richer experience you could:

- Implement additional backgrounds and feats inspired by D&D 2024 rules【885722936521575†L45-L97】.
- Expand the encounter system with more diverse abilities and consequences.
- Introduce resources such as chakra, jutsu or weapons with unique properties【302656013783284†L340-L398】.
- Create a graphical interface using a GUI library.

Feel free to fork this branch and build upon it!
