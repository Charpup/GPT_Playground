"""
Naruto Ch\u016bnin Exam Text\u2011Adventure
===============================

This script implements a lightweight text‑based adventure that follows
the outline of the Ch\u016bnin Exam arc from the *Naruto* anime and manga.
It adapts mechanics from the 2024/5.5 edition of Dungeons & Dragons
in order to provide a familiar dice‑rolling experience. Players create
characters, assign ability scores from the standard array (16, 14, 13, 12,
10, 8), and use those scores to make checks against
Difficulty Classes (DCs) during each phase of the exam. Each player
starts with one point of heroic inspiration, allowing a re‑roll of any
one d20 test once per session.

Usage:
    Run `python3 naruto_game.py` in a Python interpreter. Follow the
    on‑screen prompts to create between one and three characters and
    progress through the exams. The Dungeon Master (DM) logic is
    embedded in the script and automatically adjudicates outcomes.

This file is intended to be committed to a GitHub repository as part
of a demonstration project. Feel free to modify or extend it
for your own automated game designs.
"""

import random
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


def roll_die(sides: int = 20) -> int:
    """Roll a single die with the given number of sides."""
    return random.randint(1, sides)


def ability_modifier(score: int) -> int:
    """Compute the ability modifier from an ability score."""
    return (score - 10) // 2


@dataclass
class Character:
    """Represents a player character in the Naruto game."""

    name: str
    stats: Dict[str, int] = field(default_factory=dict)
    hit_points: int = 10
    inspiration: int = 1  # Each character starts with one heroic inspiration

    def __post_init__(self) -> None:
        if not self.stats:
            standard_array = [16, 14, 13, 12, 10, 8]
            abilities = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
            self.stats = {ability: score for ability, score in zip(abilities, standard_array)}

    def make_check(self, ability: str, dc: int) -> Tuple[bool, int]:
        base_roll = roll_die()
        total = base_roll + ability_modifier(self.stats.get(ability, 10))
        return total >= dc, total

    def spend_inspiration(self) -> bool:
        if self.inspiration > 0:
            self.inspiration -= 1
            return True
        return False


class DM:
    """Represents the automated Dungeon Master controlling the story."""

    def __init__(self, players: List[Character]):
        self.players = players

    def narrate(self, text: str) -> None:
        print("\n" + text)
        print("-" * len(text))

    def prompt_choice(self, prompt: str, choices: List[str]) -> str:
        print(prompt)
        for idx, choice in enumerate(choices, 1):
            print(f"  {idx}. {choice}")
        while True:
            try:
                selection = int(input("Enter the number of your choice: "))
                if 1 <= selection <= len(choices):
                    return choices[selection - 1]
                else:
                    print("Invalid selection. Try again.")
            except ValueError:
                print("Please enter a number.")

    def stage_written_test(self) -> None:
        self.narrate(
            "Phase 1: The Written Test\n"
            "You and your team are seated in a classroom with dozens of other genin.\n"
            "The proctor warns that cheating is permitted but getting caught will result in your team's elimination.\n"
            "You'll need to pass a series of increasingly difficult questions without drawing attention."
        )
        dc = 12
        for character in self.players:
            self.narrate(f"{character.name}, it's your turn to take the test.")
            cheat = self.prompt_choice(
                "Do you attempt to cheat by copying answers using your ninja prowess?",
                ["Yes, attempt to cheat", "No, rely on your intelligence"]
            )
            if cheat.startswith("Yes"):
                success, total = character.make_check("DEX", dc)
                if not success:
                    self.narrate(
                        f"You rolled {total}. A Ch\u016bnin spots your wandering eyes. Your team loses points!"
                    )
                    if character.inspiration > 0:
                        character.inspiration -= 1
                    continue
                else:
                    self.narrate(
                        f"You smoothly copy answers without being noticed. You rolled {total}."
                    )
            else:
                success, total = character.make_check("INT", dc)
                if not success:
                    self.narrate(
                        f"{character.name} fails the question with a roll of {total}."
                    )
                    if character.inspiration > 0:
                        spend = self.prompt_choice(
                            "Would you like to spend your heroic inspiration to re\u2011roll?",
                            ["Yes", "No"]
                        )
                        if spend == "Yes" and character.spend_inspiration():
                            success, total = character.make_check("INT", dc)
                            if success:
                                self.narrate(
                                    f"Using your inspiration, you succeed with a roll of {total}!"
                                )
                            else:
                                self.narrate(
                                    f"Even with a second effort, you roll {total} and fail."
                                )
                        else:
                            self.narrate("You decline to use inspiration.")
                else:
                    self.narrate(
                        f"You answer confidently. Your roll of {total} beats the DC."
                    )

        self.narrate(
            "After the final question, Ibiki asks if anyone wishes to withdraw.\n"
            "Following Naruto's example, you refuse to give up.\n"
            "Your determination earns you passage to the next round!"
        )

    def encounter(self, character: Character, dc: int, description: str, ability: str) -> bool:
        self.narrate(description)
        success, total = character.make_check(ability, dc)
        if success:
            self.narrate(f"Success! {character.name} rolled {total} against DC {dc}.")
        else:
            self.narrate(f"Failure. {character.name} rolled {total} against DC {dc}.")
            if character.inspiration > 0:
                spend = self.prompt_choice(
                    f"{character.name}, would you like to spend inspiration to re\u2011roll?",
                    ["Yes", "No"]
                )
                if spend == "Yes" and character.spend_inspiration():
                    success, total = character.make_check(ability, dc)
                    if success:
                        self.narrate(
                            f"Using inspiration, you succeed with a roll of {total}!"
                        )
                    else:
                        self.narrate(
                            f"Even with inspiration, you fail with a roll of {total}."
                        )
        return success

    def stage_forest_of_death(self) -> None:
        self.narrate(
            "Phase 2: The Forest of Death\n"
            "Your team enters a deadly forest filled with traps, rival teams and giant creatures.\n"
            "To advance, you must retrieve both Heaven and Earth scrolls while surviving for five days."
        )
        for character in self.players:
            self.narrate(f"{character.name}'s journey through the forest begins...")
            self.encounter(
                character, dc=14,
                description="A giant snake lunges from the trees! You must dodge its attack.",
                ability="DEX",
            )
            self.encounter(
                character, dc=15,
                description="A rival team ambushes you. Can you out\u2011smart them?",
                ability="INT",
            )
            self.encounter(
                character, dc=13,
                description="The sinister Orochimaru inflicts a cursed seal. You resist the fear.",
                ability="WIS",
            )
            self.narrate(f"{character.name} survives the Forest of Death!\n")

    def stage_preliminaries(self) -> None:
        self.narrate(
            "Phase 3: Preliminary Matches\n"
            "After surviving the forest, too many teams remain. The proctors organize one\u2011on\u2011one preliminaries.\n"
            "Winning a match secures your spot in the final tournament."
        )
        for character in self.players:
            self.narrate(f"{character.name}, you step into the arena for your match...")
            wins = 0
            for round_no in range(1, 4):
                success = self.encounter(
                    character, dc=15,
                    description=f"Round {round_no}: You exchange blows with a formidable foe.",
                    ability="STR",
                )
                if success:
                    wins += 1
                if wins >= 2:
                    break
            if wins >= 2:
                self.narrate(f"{character.name} wins the preliminary match!")
            else:
                self.narrate(f"{character.name} is defeated in the preliminaries.")

    def run_game(self) -> None:
        self.stage_written_test()
        self.stage_forest_of_death()
        self.stage_preliminaries()
        self.narrate("Your adventure concludes. Thank you for playing!")


def main() -> None:
        print("Welcome to the Naruto Ch\u016bnin Exam Adventure!")
        while True:
            try:
                num_players = int(input("Enter number of players (1\u20113): "))
                if 1 <= num_players <= 3:
                    break
                else:
                    print("Please enter a number between 1 and 3.")
            except ValueError:
                print("Please enter a valid integer.")
        players: List[Character] = []
        for i in range(num_players):
            name = input(f"Enter name for player {i + 1}: ") or f"Player{i + 1}"
            character = Character(name=name)
            players.append(character)
        dm = DM(players)
        dm.run_game()


if __name__ == "__main__":
    main()
