"""Dice rolling utilities for the Naruto-inspired tabletop adventure."""

from dataclasses import dataclass
import random
from typing import Callable, Tuple


@dataclass
class RollResult:
    """Represents the outcome of a single dice roll."""

    total: int
    detail: str

    def __str__(self) -> str:
        return f"{self.total} ({self.detail})"


def roll_die(sides: int, rng: random.Random) -> int:
    return rng.randint(1, sides)


def roll_dice(count: int, sides: int, rng: random.Random) -> Tuple[int, str]:
    rolls = [roll_die(sides, rng) for _ in range(count)]
    return sum(rolls), "+".join(str(r) for r in rolls)


def ability_modifier(score: int) -> int:
    return (score - 10) // 2


def ability_check(modifier: int, dc: int, rng: random.Random, proficiency: int = 0) -> RollResult:
    roll = roll_die(20, rng)
    total = roll + modifier + proficiency
    detail = f"d20:{roll}+mod:{modifier}+prof:{proficiency}"
    success = total >= dc
    outcome = "success" if success else "fail"
    return RollResult(total=total, detail=f"{detail} -> {outcome} vs DC {dc}")


def damage_roll(dice: str, rng: random.Random) -> RollResult:
    count, sides = (int(part) for part in dice.lower().split("d"))
    total, detail = roll_dice(count, sides, rng)
    return RollResult(total=total, detail=f"{detail} ({dice})")


def ask_use_inspiration(has_inspiration: bool, prompt_fn: Callable[[str], str]) -> bool:
    if not has_inspiration:
        return False
    choice = prompt_fn("你要消耗英雄灵感重掷这个检定吗？(y/N): ").strip().lower()
    return choice == "y"
