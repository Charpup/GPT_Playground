"""Final tournament and Konoha Crush climax."""

import random

from ..character import Character
from ..dice import ability_check
from ..combat import duel
from ..prompt import announce, Prompt
from ..inspiration import with_inspiration


def _naruto_vs_neji(character: Character, rng: random.Random, prompt_fn: Prompt) -> bool:
    announce("鸣人 vs 宁次（命运之战）")
    trick = with_inspiration(
        character,
        lambda: ability_check(character.modifier("知识"), 14, rng, character.proficiency),
        prompt_fn,
    )
    print(f"影分身战术检定：{trick}")
    neji = ability_check(character.modifier("意志"), 13, rng)
    print(f"鼓舞鸣人的演讲检定：{neji}")
    win = trick.total >= 14 or neji.total >= 13
    if win:
        print("鸣人在你的策略帮助下突破八卦掌，胜利！")
        character.hero_inspiration = True
    else:
        print("宁次预判了你的招式，鸣人被压制。")
    return win


def _shikamaru_vs_temari(character: Character, rng: random.Random, prompt_fn: Prompt) -> bool:
    announce("鹿丸 vs 手鞠（智斗风镰）")
    shadow = ability_check(character.modifier("感知"), 14, rng, character.proficiency)
    print(f"影子规划检定：{shadow}")
    if shadow.total >= 14:
        print("你的烟雾弹与影缝配合让鹿丸轻松投降，保存体力。")
        return True
    print("影子长度不足，鹿丸主动认输。你记录了手鞠的风压数据。")
    return False


def _gaara_showdown(character: Character, rng: random.Random, prompt_fn: Prompt) -> bool:
    announce("佐助 vs 我爱罗（崩坏导火索）")
    blitz = duel(
        character,
        rng,
        dc=15,
        opponent="尾兽化的我爱罗",
        prompt_fn=prompt_fn,
        flavor="你与佐助一同冲锋，雷遁与体术并用。",
        damage="2d6",
    )
    print("大蛇丸发动木叶崩溃计划，场馆陷入混乱！")
    evacuate = ability_check(character.modifier("速度"), 12, rng, character.proficiency)
    print(f"撤离观众与护送雏田检定：{evacuate}")
    if evacuate.total < 12:
        character.gain_fatigue()
        print("混乱中你消耗过大，疲劳 +1。")
    return bool(blitz)


def run_finals(character: Character, rng: random.Random, prompt_fn: Prompt) -> bool:
    announce("决赛与木叶崩溃事件")
    victories = 0

    victories += int(_naruto_vs_neji(character, rng, prompt_fn))
    victories += int(_shikamaru_vs_temari(character, rng, prompt_fn))
    victories += int(_gaara_showdown(character, rng, prompt_fn))

    defense_choice = prompt_fn("要加入上忍防御木叶吗？(y/N): ").strip().lower() == "y"
    if defense_choice:
        guard = with_inspiration(
            character,
            lambda: ability_check(character.modifier("体术"), 14, rng, character.proficiency),
            prompt_fn,
        )
        print(f"街区防御检定：{guard}")
        if guard.total >= 14:
            victories += 1
            print("你与旗木卡卡西并肩守住一线。英雄灵感 +1。")
            character.hero_inspiration = True
        else:
            character.gain_fatigue()
            print("你被音忍伤到，疲劳 +1。")

    if victories >= 3:
        announce("你经历所有考验，获得中忍晋升与鸣人的认可！")
        return True

    announce("虽然表现出色，但还有成长空间。考试以经验为主。")
    return False
