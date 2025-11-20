"""Prompt helpers and narration utilities for the text adventure."""

from typing import Callable, List

Prompt = Callable[[str], str]


def announce(message: str) -> None:
    print(f"\n== {message} ==")


def build_prompt(
    auto_choices: List[str],
    fallback: str | None = None,
    inspiration_fallback: str | None = None,
    force_scripted: bool = False,
) -> Prompt:
    """Create a prompt function that can be scripted for demos or tests."""

    choices = auto_choices.copy()
    scripted = bool(auto_choices) or force_scripted

    def prompt_fn(question: str) -> str:
        if choices:
            return choices.pop(0)
        if scripted and "英雄灵感" in question and inspiration_fallback is not None:
            print(f"{question}{inspiration_fallback}")
            return inspiration_fallback
        if scripted and fallback is not None:
            print(f"{question}{fallback}")
            return fallback
        return input(question)

    return prompt_fn
