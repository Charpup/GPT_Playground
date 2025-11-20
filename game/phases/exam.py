"""Written exam and mind-game phase set in the academy classroom."""

import random

from ..character import Character
from ..dice import ability_check
from ..inspiration import with_inspiration
from ..prompt import announce, Prompt


def _cheat_flow(character: Character, rng: random.Random, prompt_fn: Prompt) -> int:
    print("伊比喜的考卷难得离谱，必须要靠作弊或灵感才能通过。")
    knowledge = with_inspiration(
        character,
        lambda: ability_check(character.modifier("知识"), 15, rng, character.proficiency),
        prompt_fn,
    )
    print(f"知识检定：{knowledge}")

    cheat = prompt_fn("要尝试忍者式作弊吗？(y/N): ").strip().lower() == "y"
    success = 0
    if knowledge.total >= 15:
        success += 1
    if cheat:
        stealth = with_inspiration(
            character,
            lambda: ability_check(character.modifier("速度"), 13, rng, character.proficiency),
            prompt_fn,
        )
        print(f"隐匿作弊检定：{stealth}")
        if stealth.total < 13:
            print("你被监考抓住，罚坐半场，查克拉削半并增加 1 级疲劳。")
            character.chakra //= 2
            character.gain_fatigue()
        else:
            success += 1
    return success


def _ibiki_mind_game(character: Character, rng: random.Random, prompt_fn: Prompt) -> bool:
    print("伊比喜宣布：答错终身不得提升！全班动摇，心态检定开始。")
    will = with_inspiration(
        character,
        lambda: ability_check(character.modifier("意志"), 14, rng, character.proficiency),
        prompt_fn,
    )
    print(f"意志检定：{will}")
    if will.total < 14:
        character.gain_fatigue()
        print("压力让你发抖，疲劳 +1。")
    declaration = prompt_fn("是否像鸣人一样站起来宣誓不畏失败？(y/N): ").strip().lower() == "y"
    if declaration:
        character.hero_inspiration = True
        print("你的宣言点燃全班的斗志，获得英雄灵感！")
    return declaration or will.total >= 14


def run_exam_phase(character: Character, rng: random.Random, prompt_fn: Prompt) -> bool:
    announce("第一阶段：笔试与心理考验")
    success = _cheat_flow(character, rng, prompt_fn)
    final_question = _ibiki_mind_game(character, rng, prompt_fn)

    if success >= 1 or final_question:
        announce("你们通过了笔试，进入死亡森林阶段。")
        return True

    announce("队伍被淘汰，冒险提前结束。")
    return False
