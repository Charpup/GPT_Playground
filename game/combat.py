"""Lightweight combat and contest helpers."""

from typing import Iterable
import random

from .dice import RollResult, ability_check, damage_roll
from .character import Character
from .prompt import announce, Prompt
from .inspiration import with_inspiration


class DuelOutcome(RollResult):
    pass


def contested_check(
    character: Character,
    attacker_mod: int,
    defender_mod: int,
    dc: int,
    rng: random.Random,
    prompt_fn: Prompt,
    label: str,
) -> tuple[RollResult, RollResult]:
    """Resolve a contested check with optional inspiration on offense."""

    attack = with_inspiration(
        character,
        lambda: ability_check(attacker_mod, dc, rng, character.proficiency),
        prompt_fn,
    )
    defense = ability_check(defender_mod, dc - 1, rng)
    print(f"{label} — 进攻：{attack} / 防御：{defense}")
    return attack, defense


def duel(
    character: Character,
    rng: random.Random,
    dc: int,
    opponent: str,
    prompt_fn: Prompt,
    flavor: str = "",
    damage: str = "1d6",
) -> bool:
    """Single duel inspired by the anime bouts."""

    announce(f"对战 {opponent}")
    if flavor:
        print(flavor)
    attack, defense = contested_check(
        character,
        attacker_mod=character.modifier("体术"),
        defender_mod=character.modifier("速度"),
        dc=dc,
        rng=rng,
        prompt_fn=prompt_fn,
        label="决斗检定",
    )
    score = int(attack.total >= dc) + int(defense.total >= dc - 1)
    if score >= 2:
        print(f"你战胜了 {opponent}！")
        character.hero_inspiration = True
        return True

    injury = damage_roll(damage, rng)
    character.adjust_hp(-injury.total)
    print(f"{opponent} 更胜一筹，你受到 {injury} 伤害，当前生命 {character.hp}。")
    return False


def group_scene(
    character: Character,
    participants: Iterable[tuple[str, int, str]],
    rng: random.Random,
    prompt_fn: Prompt,
) -> int:
    """Resolve a chain of duels; return number of wins."""

    wins = 0
    for name, dc, flavor in participants:
        if duel(character, rng, dc, name, prompt_fn, flavor=flavor):
            wins += 1
        if character.hp <= 0:
            announce("伤势过重，无法继续。")
            break
    return wins
