"""Heroic inspiration utilities."""

from typing import Callable

from .dice import RollResult, ask_use_inspiration
from .character import Character
from .prompt import Prompt


def with_inspiration(
    character: Character,
    roll_fn: Callable[[], RollResult],
    prompt_fn: Prompt,
    force: bool | None = None,
) -> RollResult:
    """Roll with an optional heroic inspiration reroll."""

    first = roll_fn()
    if first.total >= 0:
        want_reroll = ask_use_inspiration(character.hero_inspiration, prompt_fn) if force is None else force
        if not want_reroll:
            return first
    if not character.hero_inspiration:
        return first
    character.hero_inspiration = False
    print("你消耗了英雄灵感，准备重掷……")
    return roll_fn()
