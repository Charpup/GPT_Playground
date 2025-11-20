"""Preliminary tournament matches inside the tower."""

import random
from typing import List, Tuple

from ..character import Character
from ..dice import ability_check
from ..combat import duel
from ..prompt import announce, Prompt


PRELIM_MATCHES: List[Tuple[str, int, str]] = [
    ("佐助 vs 叶隐药师兜支援的约鲁伊", 13, "你模仿佐助的速度切入，封住对手查克拉。"),
    ("鹿丸 vs 多由也雏形的金", 12, "你用影缝协助，鹿丸一举擒获。"),
    ("小樱 vs 井野", 11, "两人拳法互拼，你选择加油或插手救场。"),
    ("我爱罗 vs 李洛克", 15, "李开八门的光景震撼全场，你守在场边防止砂暴波及。"),
    ("鸣人 vs 牙", 12, "赤丸扑来，你用砂轮或水弹支援鸣人。"),
    ("雏田 vs 宁次", 14, "宗家与分家的对决，你护在雏田身侧。"),
    ("丁次 vs 多苏", 13, "音波再次来袭，这次你更有经验。"),
    ("志乃 vs 左近", 12, "虫群压制对手，你封锁侧翼。"),
    ("手鞠 vs 天天", 13, "风镰与忍具对撞，你能否打出破绽？"),
]


def _support_match(character: Character, rng: random.Random, prompt_fn: Prompt, match: Tuple[str, int, str]) -> bool:
    title, dc, flavor = match
    announce(title)
    print(flavor)
    aid = ability_check(character.modifier("感知"), dc, rng, character.proficiency)
    print(f"战术支援检定：{aid}")
    if aid.total >= dc:
        print("你的提醒与投掷道具改变战局，队友获胜并感谢你。英雄灵感 +1。")
        character.hero_inspiration = True
        return True
    print("你尽力支援但无力回天，记录下对手的套路。")
    return False


def run_prelims(character: Character, rng: random.Random, prompt_fn: Prompt) -> bool:
    announce("塔内预赛")
    victories = 0

    solo = prompt_fn("你要亲自出场一场对决吗？(y/N): ").strip().lower() == "y"
    if solo:
        victories += duel(
            character,
            rng,
            dc=13,
            opponent="音忍预备队员佐井",
            prompt_fn=prompt_fn,
            flavor="对手擅长墨兽术，你需要迅速拉近距离。",
            damage="1d8",
        )

    for match in PRELIM_MATCHES:
        victories += int(_support_match(character, rng, prompt_fn, match))
        if character.hp <= 0:
            announce("你的伤势无法继续观看或作战。")
            break

    if victories >= 5:
        announce("你和木叶的战友们晋级至决赛！")
        return True
    announce("你未能累积足够胜场，但获得宝贵经验与情报。")
    return False
