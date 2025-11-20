"""Forest of Death survival and landmark encounters."""

import random
from typing import List

from ..character import Character
from ..dice import ability_check, damage_roll
from ..inspiration import with_inspiration
from ..prompt import announce, Prompt


def _orochimaru_trial(character: Character, rng: random.Random, prompt_fn: Prompt) -> List[str]:
    notes: List[str] = ["巨蛇从树冠俯冲，大蛇丸的气息扑面而来！"]
    escape = with_inspiration(
        character,
        lambda: ability_check(character.modifier("速度"), 18, rng, character.proficiency),
        prompt_fn,
    )
    notes.append(f"速度检定：{escape}")
    if escape.total >= 18:
        character.hero_inspiration = True
        character.scrolls.append("蛇影卷轴")
        notes.append("你躲过蛇袭，巧妙利用烟雾弹撤离，获得英雄灵感并捡到一卷蛇影卷轴。")
        return notes

    bite = damage_roll("2d6", rng)
    character.adjust_hp(-bite.total)
    character.gain_fatigue()
    notes.append(f"你被巨蛇缠绕受到 {bite} 伤害并疲劳 +1，仍需硬抗大蛇丸的压迫。")

    will = with_inspiration(
        character,
        lambda: ability_check(character.modifier("意志"), 16, rng, character.proficiency),
        prompt_fn,
    )
    notes.append(f"意志检定（抵抗恐惧）：{will}")
    if will.total >= 16:
        character.scrolls.append("蛇影卷轴")
        notes.append("你稳住心神，逼迫大蛇丸露出兴趣，他留下蛇影卷轴作为考验。")
        character.hero_inspiration = True
    else:
        notes.append("恐惧侵蚀，你留下蛇印般的阴影，疲劳再 +1。")
        character.gain_fatigue()
    return notes


def _team_dosu(character: Character, rng: random.Random, prompt_fn: Prompt) -> List[str]:
    notes: List[str] = ["音忍三人组多苏、左近和鬼童丸样的索拉米突然包围你。"]
    clash = with_inspiration(
        character,
        lambda: ability_check(character.modifier("体术"), 15, rng, character.proficiency),
        prompt_fn,
    )
    notes.append(f"体术对抗：{clash}")
    if clash.total >= 15:
        character.scrolls.append("夺来的卷轴")
        character.hero_inspiration = True
        notes.append("你用体术和替身术打乱音波攻势，夺下一卷。")
    else:
        sonic = damage_roll("1d8", rng)
        character.adjust_hp(-sonic.total)
        notes.append(f"多苏的斩空音波命中，你受到 {sonic} 伤害。")
        retreat = ability_check(character.modifier("速度"), 12, rng, character.proficiency)
        notes.append(f"撤退检定：{retreat}")
        if retreat.total < 12:
            character.gain_fatigue()
            notes.append("勉强撤退，疲劳 +1。")
    return notes


def _ally_kabuto(character: Character, rng: random.Random) -> List[str]:
    notes = ["药师兜现身，他递来查克拉恢复丸并分享地图。"]
    heal = damage_roll("1d6", rng)
    character.adjust_hp(heal.total)
    character.chakra += 3
    notes.append(f"恢复 {heal.total} 生命与 3 点查克拉。")
    return notes


def _gaara_pressure(character: Character, rng: random.Random) -> List[str]:
    notes = ["我爱罗在树顶冷眼旁观，砂之守鹤的气息让人窒息。"]
    stare = ability_check(character.modifier("意志"), 15, rng, character.proficiency)
    notes.append(f"意志检定：{stare}")
    if stare.total >= 15:
        notes.append("你直视他而不退缩，砂之守鹤收起兴趣。英雄灵感 +1。")
        character.hero_inspiration = True
    else:
        notes.append("你下意识后退，团队士气略降。疲劳 +1。")
        character.gain_fatigue()
    return notes


def _random_patrol(character: Character, rng: random.Random) -> List[str]:
    roll = rng.randint(1, 6)
    notes: List[str] = [f"d6 掷出 {roll}"]
    if roll in (1, 2):
        notes.append("遇到同村考生，互换补给并讨论卷轴。")
        character.adjust_hp(1)
        character.chakra += 1
    elif roll == 3:
        notes.append("踩中陷阱，苦无乱飞！")
        harm = damage_roll("1d6", rng)
        character.adjust_hp(-harm.total)
        if harm.total >= 4:
            character.gain_fatigue()
            notes.append("伤势不轻，疲劳 +1。")
    elif roll == 4:
        notes.extend(_team_dosu(character, rng, lambda q: "n"))
    elif roll == 5:
        notes.extend(_ally_kabuto(character, rng))
    else:
        notes.extend(_gaara_pressure(character, rng))
    return notes


def run_forest_phase(character: Character, rng: random.Random, prompt_fn: Prompt) -> bool:
    announce("第二阶段：死亡森林")
    print("安可御手洗抛出血腥警告，倒计时开始。")
    character.scrolls.append("起始卷轴")

    set_piece = prompt_fn("要主动追击卷轴 (p) 还是先潜伏侦察 (s)？ ").strip().lower() or "s"
    if set_piece == "p":
        for note in _team_dosu(character, rng, prompt_fn):
            print("-", note)
    else:
        print("你在树梢潜伏，等待最佳时机。")

    print("\n【设定事件】大蛇丸的袭击逼近……")
    for note in _orochimaru_trial(character, rng, prompt_fn):
        print("-", note)
    if character.hp <= 0 or character.fatigue >= 5:
        announce("你倒在蛇压下，无缘后续考试。")
        return False

    for day in range(1, 4):
        print(f"\n第 {day} 天 —— 生命 {character.hp}，查克拉 {character.chakra}，疲劳 {character.fatigue}")
        choice = prompt_fn("行动：探索 (e) / 埋伏 (a) / 休息 (r): ").strip().lower() or "e"
        if choice == "r":
            character.rest()
            print("你封印伤口，恢复少量生命和查克拉，疲劳 -1。")
        else:
            for note in _random_patrol(character, rng):
                print("-", note)
        if character.hp <= 0:
            announce("重伤倒地，考试失败。")
            return False

    scroll_count = len([s for s in character.scrolls if "卷轴" in s])
    if scroll_count >= 2:
        announce("你成功收集到天与地的卷轴，抵达终点塔！")
        return True

    announce("卷轴不足，是否赌上意志展示忍道？需要 DC 15 的意志检定。")
    gamble = with_inspiration(
        character,
        lambda: ability_check(character.modifier("意志"), 15, rng, character.proficiency),
        prompt_fn,
    )
    print(f"忍道检定：{gamble}")
    if gamble.total >= 15:
        character.gain_fatigue()
        announce("你的宣言打动了考官，疲劳 1 级但准许进入塔内。")
        return True

    announce("卷轴不足，无法进入下一阶段。")
    return False
