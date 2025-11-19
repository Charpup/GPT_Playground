"""Story events and automated DM logic."""

import random
from typing import Callable, List, Tuple

from .character import Character
from .dice import RollResult, ability_check, ask_use_inspiration

Prompt = Callable[[str], str]


def announce(message: str) -> None:
    print(f"\n== {message} ==")


def with_inspiration(
    character: Character,
    roll_fn: Callable[[], RollResult],
    prompt_fn: Prompt,
) -> RollResult:
    first = roll_fn()
    if first.total >= 0 and not ask_use_inspiration(character.hero_inspiration, prompt_fn):
        return first
    if not character.hero_inspiration:
        return first
    character.hero_inspiration = False
    print("你消耗了英雄灵感，准备重掷……")
    return roll_fn()


def exam_phase(character: Character, rng: random.Random, prompt_fn: Prompt) -> bool:
    announce("第一阶段：笔试与心理考验")
    result = with_inspiration(
        character,
        lambda: ability_check(character.modifier("知识"), 15, rng, character.proficiency),
        prompt_fn,
    )
    print(f"知识检定结果：{result}")

    cheat = prompt_fn("要尝试作弊吗？(y/N): ").strip().lower() == "y"
    if cheat:
        stealth = with_inspiration(
            character,
            lambda: ability_check(character.modifier("速度"), 13, rng, character.proficiency),
            prompt_fn,
        )
        print(f"作弊/隐匿检定：{stealth}")
        if stealth.total < 13:
            print("你被监考发现，队伍受到警告并失去一半查克拉！")
            character.chakra //= 2
            character.gain_fatigue()

    declaration = prompt_fn("是否像鸣人一样宣誓不畏失败？(y/N): ").strip().lower() == "y"
    if declaration:
        character.hero_inspiration = True
        print("你的意志感染全场，获得英雄灵感！")

    correct_answers = 0
    if result.total >= 15:
        correct_answers += 1
    if not cheat or (cheat and result.total >= 10):
        correct_answers += 1
    passed = correct_answers >= 1 or declaration
    if passed:
        announce("你们通过了笔试，进入死亡森林阶段。")
    else:
        announce("队伍被淘汰，冒险提前结束。")
    return passed


def random_forest_event(character: Character, rng: random.Random) -> Tuple[str, List[str]]:
    roll = rng.randint(1, 6)
    notes: List[str] = []
    if roll == 1:
        notes.append("友军遇见：同村忍者与你共享情报，恢复少量生命。")
        character.adjust_hp(2)
    elif roll == 2:
        notes.append("敌对队伍伏击！")
        attack = ability_check(character.modifier("体术"), 12, rng, character.proficiency)
        notes.append(f"近身对抗：{attack}")
        if attack.total < 12:
            damage = -rng.randint(1, 6)
            character.adjust_hp(damage)
            notes.append(f"你受伤 {abs(damage)} 点并获得 1 级疲劳。")
            character.gain_fatigue()
        else:
            character.scrolls.append("夺取的卷轴")
            notes.append("你击退敌人并夺取了卷轴。")
    elif roll == 3:
        notes.append("环境陷阱：需要体魄检定躲避。")
        save = ability_check(character.modifier("体魄"), 14, rng)
        notes.append(f"体魄检定：{save}")
        if save.total < 14:
            character.adjust_hp(-rng.randint(1, 6))
            character.gain_fatigue()
            notes.append("你受到伤害并精疲力竭。")
    elif roll == 4:
        notes.append("隐藏卷轴：探索可获得资源。")
        search = ability_check(character.modifier("感知"), 13, rng, character.proficiency)
        notes.append(f"探索检定：{search}")
        if search.total >= 13:
            character.scrolls.append("隐藏卷轴")
            character.chakra += 2
            notes.append("你成功找到卷轴并恢复 2 点查克拉。")
    elif roll == 5:
        notes.append("遭遇大蛇丸的幻影！")
        escape = ability_check(character.modifier("速度"), 18, rng, character.proficiency)
        notes.append(f"速度检定：{escape}")
        if escape.total < 18:
            character.adjust_hp(-rng.randint(3, 8))
            character.gain_fatigue()
            notes.append("你艰难逃脱，身受重伤。")
        else:
            character.hero_inspiration = True
            notes.append("你智取大蛇丸，获得英雄灵感。")
    else:
        notes.append("幻术试炼：需要意志检定。")
        will = ability_check(character.modifier("意志"), 15, rng, character.proficiency)
        notes.append(f"意志检定：{will}")
        if will.total >= 15:
            character.hero_inspiration = True
            notes.append("你看破幻术，收获英雄灵感。")
        else:
            character.gain_fatigue()
            notes.append("你被幻术困扰，疲劳加重。")
    return f"d6 掷出 {roll}", notes


def forest_phase(character: Character, rng: random.Random, prompt_fn: Prompt) -> bool:
    announce("第二阶段：死亡森林")
    for day in range(1, 4):
        print(f"\n第 {day} 天，你的生命值 {character.hp}，查克拉 {character.chakra}，疲劳 {character.fatigue}")
        choice = prompt_fn("选择行动：探索 (e) / 埋伏 (a) / 休息 (r): ").strip().lower() or "e"
        if choice == "r":
            character.rest()
            print("你专注恢复，生命与查克拉小幅回升。")
        else:
            table_roll, notes = random_forest_event(character, rng)
            print(table_roll)
            for note in notes:
                print("-", note)
        if character.fatigue >= 6 or character.hp <= 0:
            announce("你在死亡森林中力竭倒下，考试失败。")
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


def duel(character: Character, rng: random.Random, dc: int, opponent: str) -> bool:
    announce(f"对战 {opponent}")
    attack = ability_check(character.modifier("体术"), dc, rng, character.proficiency)
    defense = ability_check(character.modifier("速度"), dc - 1, rng)
    print(f"进攻检定：{attack}")
    print(f"防御检定：{defense}")
    score = 0
    if attack.total >= dc:
        score += 1
    if defense.total >= dc - 1:
        score += 1
    if character.hero_inspiration and score == 1:
        if ask_use_inspiration(True, lambda prompt: "y"):
            character.hero_inspiration = False
            extra = ability_check(character.modifier("意志"), 12, rng)
            print(f"灵感驱动的意志检定：{extra}")
            if extra.total >= 12:
                score += 1
    if score >= 2:
        print(f"你战胜了 {opponent}！")
        character.hero_inspiration = True
        return True
    print(f"{opponent} 更胜一筹，你败下阵来。")
    character.adjust_hp(-rng.randint(1, 6))
    return False


def tournament_phase(character: Character, rng: random.Random) -> bool:
    announce("第三阶段：淘汰赛与决赛")
    opponents = [(12, "砂隐风使"), (14, "我爱罗的砂")]
    victories = 0
    for dc, name in opponents:
        if duel(character, rng, dc, name):
            victories += 1
        if character.hp <= 0:
            announce("伤势过重，无法继续比赛。")
            break
    if victories == len(opponents):
        announce("你夺得胜利，晋升为中忍！")
        return True
    announce("虽然未能夺冠，但你获得了宝贵的经验。")
    return False


def build_prompt(
    auto_choices: List[str],
    fallback: str | None = None,
    inspiration_fallback: str | None = None,
    force_scripted: bool = False,
) -> Prompt:
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


def run_game(
    seed: int | None = None,
    scripted_choices: List[str] | None = None,
    demo_mode: bool = False,
) -> None:
    rng = random.Random(seed)
    prompt_fn = build_prompt(
        scripted_choices or [],
        fallback="e" if demo_mode else None,
        inspiration_fallback="y" if demo_mode else None,
        force_scripted=demo_mode,
    )
    announce("欢迎来到火影忍者：中忍考试篇 (文字版)")
    name = prompt_fn("角色名（默认：新晋忍者）: ").strip() or "新晋忍者"
    archetype = prompt_fn("职业选择 体术专家(t) / 忍术专家(n) / 幻术/医疗专家(g): ").strip().lower()
    archetype_name = {"t": "体术专家", "n": "忍术专家", "g": "幻术/医疗专家"}.get(archetype, "体术专家")
    background_choice = prompt_fn("背景 木叶(k) / 砂隐(s) / 音忍(o): ").strip().lower()
    background_name = {"k": "木叶村天赋", "s": "砂隐之村训练", "o": "音忍村研究"}.get(background_choice, "木叶村天赋")

    from .character import build_ability_scores

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

    if not exam_phase(character, rng, prompt_fn):
        return
    if not forest_phase(character, rng, prompt_fn):
        return
    tournament_phase(character, rng)


if __name__ == "__main__":
    run_game()
