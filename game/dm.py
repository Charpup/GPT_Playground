"""Campaign runner orchestrating each phase."""

import random
from typing import List

from .character import Character, build_ability_scores
from .prompt import announce, build_prompt, Prompt
from .phases.exam import run_exam_phase
from .phases.forest import run_forest_phase
from .phases.prelims import run_prelims
from .phases.finals import run_finals


def create_character(prompt_fn: Prompt) -> Character:
    name = prompt_fn("角色名（默认：新晋忍者）: ").strip() or "新晋忍者"
    archetype = prompt_fn("职业选择 体术专家(t) / 忍术专家(n) / 幻术/医疗专家(g): ").strip().lower()
    archetype_name = {"t": "体术专家", "n": "忍术专家", "g": "幻术/医疗专家"}.get(archetype, "体术专家")
    background_choice = prompt_fn("背景 木叶(k) / 砂隐(s) / 音忍(o): ").strip().lower()
    background_name = {"k": "木叶村天赋", "s": "砂隐之村训练", "o": "音忍村研究"}.get(background_choice, "木叶村天赋")

    abilities = build_ability_scores(archetype_name, background_name)
    character = Character(
        name=name,
        archetype=archetype_name,
        background=background_name,
        ability_scores=abilities,
        hero_inspiration=background_name == "木叶村天赋",
    )

    print(f"\n{name}，{background_name}出身的{archetype_name}，能力值：{abilities}")
    print(f"生命值 {character.hp}，查克拉 {character.chakra}，英雄灵感 {character.hero_inspiration}")
    return character


def run_game(
    seed: int | None = None,
    scripted_choices: List[str] | None = None,
    demo_mode: bool = False,
) -> None:
    rng = random.Random(seed)
    prompt_fn = build_prompt(
        scripted_choices or [],
        fallback="y" if demo_mode else None,
        inspiration_fallback="y" if demo_mode else None,
        force_scripted=demo_mode,
    )
    announce("欢迎来到火影忍者：中忍考试篇 (文字版)")
    character = create_character(prompt_fn)

    if not run_exam_phase(character, rng, prompt_fn):
        return
    if not run_forest_phase(character, rng, prompt_fn):
        return
    if not run_prelims(character, rng, prompt_fn):
        return
    run_finals(character, rng, prompt_fn)
