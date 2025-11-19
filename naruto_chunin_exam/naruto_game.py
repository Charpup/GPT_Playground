"""
火影忍者·中忍考试：文字冒险游戏
==============================

本脚本是对《火影忍者》中中忍考试篇的一个大幅扩展，
使用 2024/5.5 版 DND 规则作为判定机制，
提供完整的中文交互剧情和决策点。玩家可以在笔试、死亡森林、
预赛以及决赛各个阶段自由抉择，点数和掷骰由程序自动计算，
无需手动记录。

要运行此游戏，请确保已安装 Python 3，
然后在命令行中执行：

```
python3 naruto_chunin_exam/naruto_game.py
```

脚本将引导您创建 1–3 名角色（不足 3 人时会自动生成 NPC），
随后进入考试流程。建议在终端窗口运行，以获得良好的输入提示。
"""

import random
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple


def roll_die(sides: int = 20) -> int:
    """掷一个拥有给定面数的骰子。"""
    return random.randint(1, sides)


def ability_modifier(score: int) -> int:
    """根据属性值计算修正值。"""
    return (score - 10) // 2


ABILITIES = ["力量", "敏捷", "体质", "智力", "感知", "魅力"]


@dataclass
class Character:
    """表示游戏中的玩家角色。"""

    name: str
    stats: Dict[str, int] = field(default_factory=dict)
    hit_points: int = 10
    inspiration: int = 1  # 每个角色初始拥有 1 点英雄灵感
    fatigue: int = 0  # 疲劳层级，影响后续检定
    scrolls: Set[str] = field(default_factory=set)  # 收集的天/地卷轴
    winner: bool = True  # 用于记录是否晋级到决赛

    def __post_init__(self) -> None:
        # 如果未提供属性，则使用标准数组自动分配
        if not self.stats:
            standard_array = [16, 14, 13, 12, 10, 8]
            self.stats = {ability: score for ability, score in zip(ABILITIES, standard_array)}

    def make_check(self, ability: str, dc: int) -> Tuple[bool, int]:
        """进行一次属性检定并返回是否成功和总点数。"""
        base = roll_die()
        total = base + ability_modifier(self.stats.get(ability, 10)) - self.fatigue
        success = total >= dc
        return success, total

    def spend_inspiration(self) -> bool:
        """消耗英雄灵感，返回是否成功消耗。"""
        if self.inspiration > 0:
            self.inspiration -= 1
            return True
        return False

    def rest(self) -> None:
        """休息一轮，恢复 1 点疲劳。"""
        if self.fatigue > 0:
            self.fatigue -= 1


class DM:
    """自动 DM 类，控制故事流程和检定。"""

    def __init__(self, players: List[Character]):
        # 补充 NPC 使队伍达到 3 人
        npc_names = ["佐井", "雏田", "李洛克", "志乃", "天天"]
        while len(players) < 3:
            npc_name = npc_names.pop(0)
            players.append(Character(name=npc_name))
        self.players = players
        self.day = 1  # 死亡森林中当前天数

    def narrate(self, text: str) -> None:
        """输出叙述文字并分隔。"""
        print("\n" + text)
        print("-" * len(text))

    def prompt_choice(self, prompt: str, choices: List[str]) -> str:
        """提示玩家在多个选项中做出选择。"""
        print(prompt)
        for idx, choice in enumerate(choices, 1):
            print(f"  {idx}. {choice}")
        while True:
            try:
                selection = int(input("请输入选项编号: "))
                if 1 <= selection <= len(choices):
                    return choices[selection - 1]
                print("输入无效，请重新选择。")
            except ValueError:
                print("请输入数字。")

    def stage_intro(self) -> None:
        """开始阶段：介绍背景并组队。"""
        self.narrate(
            "欢迎来到中忍考试！木叶村与其他忍村共同举办的考试即将开始。\n"
            "你们作为一支三人小队，将面对艰难的挑战。相信自己的忍道，展开冒险吧！"
        )

    def stage_written_test(self) -> None:
        """笔试阶段，包括作弊、答题和宣誓。"""
        self.narrate(
            "阶段一：笔试\n"
            "监考官宣布，本次考试可以作弊但若被发现全队淘汰。你们必须回答九道难题，\n"
            "并在最后的选择题中展现勇气。"
        )
        # 每个玩家答题
        for ch in self.players:
            self.narrate(f"{ch.name} 正在回答试题。")
            # 先决定是否作弊
            action = self.prompt_choice(
                "你是否选择作弊以获取答案？",
                ["是，悄悄作弊", "否，凭自己的知识作答"],
            )
            if action.startswith("是"):
                # 作弊需要敏捷检定，失败则失去灵感或受罚
                success, total = ch.make_check("敏捷", 13)
                if success:
                    self.narrate(f"你身手矫健，没有被监考发现，检定结果 {total} >= 13。你顺利抄到了答案。")
                else:
                    self.narrate(f"糟糕！你被监考察觉，检定结果 {total} < 13。监考扣除了你的一点英雄灵感作为惩罚。")
                    if ch.inspiration > 0:
                        ch.inspiration -= 1
            else:
                # 知识检定难度 15
                success, total = ch.make_check("智力", 15)
                if success:
                    self.narrate(f"你凭借扎实的知识顺利答题，检定结果 {total} >= 15。")
                else:
                    self.narrate(f"你的知识有欠缺，检定结果 {total} < 15。")
                    if ch.inspiration > 0:
                        # 提示是否使用灵感重掷
                        use_insp = self.prompt_choice(
                            "是否消耗英雄灵感重掷？", ["是", "否"],
                        )
                        if use_insp == "是" and ch.spend_inspiration():
                            success, total = ch.make_check("智力", 15)
                            if success:
                                self.narrate(f"重掷后成功！你获得了 {total}，通过了检定。")
                            else:
                                self.narrate(f"很遗憾，重掷后仍未通过，结果 {total}。")
        # 最后一题
        self.narrate(
            "监考官宣布最后一题：若答错，将永远失去参赛资格；若放弃，将立刻淘汰。\n"
            "你们是否选择坚持到底？"
        )
        decision = self.prompt_choice("做出选择：", ["坚持，不畏失败", "退出这场考试"])
        if decision.startswith("坚持"):
            self.narrate(
                "你们无所畏惧，坚持自己的信念。监考官满意地点点头，宣布所有坚持者通过此阶段！"
            )
            # 奖励每位角色一点灵感
            for ch in self.players:
                ch.inspiration += 1
        else:
            self.narrate(
                "你们选择退出考试。故事在此结束。感谢参与！"
            )
            # 标记游戏结束
            for ch in self.players:
                ch.winner = False

    def random_forest_event(self, ch: Character) -> None:
        """根据随机结果触发森林中的事件。"""
        roll = random.randint(1, 6)
        if roll == 1:
            # 友军遭遇
            self.narrate(
                f"{ch.name} 遇到了一支友方队伍，可以进行交流。"
            )
            choice = self.prompt_choice(
                "你想要做什么？", ["交换情报和物资", "避免接触继续前进"],
            )
            if choice.startswith("交换"):
                success, total = ch.make_check("魅力", 12)
                if success:
                    self.narrate(f"交流顺利，检定 {total} >= 12，你从对方那里获得了一卷缺失的卷轴。")
                    # 随机获得天或地卷轴
                    scroll = random.choice(["天", "地"])
                    ch.scrolls.add(scroll)
                else:
                    self.narrate(f"对方态度冷淡，检定 {total} < 12，未能取得收获。")
        elif roll == 2:
            # 敌队伏击
            self.narrate(
                f"{ch.name} 被一支敌对队伍埋伏，必须战斗或谈判。"
            )
            choice = self.prompt_choice("你的应对？", ["战斗", "谈判"])
            if choice == "战斗":
                success, total = ch.make_check("力量", 14)
                if success:
                    self.narrate(f"你击败了敌队，检定 {total} >= 14，夺得了一卷卷轴。")
                    ch.scrolls.add(random.choice(["天", "地"]))
                else:
                    self.narrate(f"你未能战胜敌人，检定 {total} < 14，被迫撤退并受到 1 点疲劳。")
                    ch.fatigue += 1
            else:
                success, total = ch.make_check("魅力", 14)
                if success:
                    self.narrate(f"谈判成功，检定 {total} >= 14，双方和平分开。")
                else:
                    self.narrate(f"谈判破裂，检定 {total} < 14，你受到伤害并失去一点灵感。")
                    if ch.inspiration > 0:
                        ch.inspiration -= 1
        elif roll == 3:
            # 环境险境
            self.narrate(
                f"{ch.name} 遭遇环境陷阱，需要躲避毒沼和捕兽夹。"
            )
            success, total = ch.make_check("敏捷", 14)
            if success:
                self.narrate(f"你灵巧地躲开了陷阱，检定 {total} >= 14，无伤通过。")
            else:
                self.narrate(f"你失足落入陷阱，检定 {total} < 14，受到 1d6 伤害并累积疲劳。")
                damage = random.randint(1, 6)
                ch.hit_points -= damage
                ch.fatigue += 1
        elif roll == 4:
            # 隐藏卷轴
            self.narrate(
                f"{ch.name} 发现一个隐藏的卷轴箱，需要细心探索。"
            )
            success, total = ch.make_check("感知", 13)
            if success:
                scroll = random.choice(["天", "地"])
                ch.scrolls.add(scroll)
                self.narrate(f"你成功找到卷轴【{scroll}】，检定 {total} >= 13。")
            else:
                self.narrate(f"你搜索失败，检定 {total} < 13，错过了机会。")
        elif roll == 5:
            # 大蛇丸伏击
            self.narrate(
                f"{ch.name} 感受到了令人胆寒的气息，大蛇丸出现了！你选择？"
            )
            choice = self.prompt_choice("你的决定：", ["勇敢应战", "拼命逃跑"])
            if choice == "勇敢应战":
                success, total = ch.make_check("力量", 18)
                if success:
                    self.narrate(f"难以置信！你对抗大蛇丸竟有奇效，检定 {total} >= 18，得以保命。")
                else:
                    self.narrate(f"力量悬殊，检定 {total} < 18，你受到了重创并增加两级疲劳。")
                    ch.hit_points -= random.randint(4, 8)
                    ch.fatigue += 2
            else:
                success, total = ch.make_check("敏捷", 18)
                if success:
                    self.narrate(f"你速度惊人，检定 {total} >= 18，成功逃离大蛇丸。")
                else:
                    self.narrate(f"逃跑失败，检定 {total} < 18，你被施加诅咒并增加两级疲劳。")
                    ch.fatigue += 2
        else:
            # 幻术试炼
            self.narrate(
                f"{ch.name} 被卷入幻术，需要突破内心的恐惧。"
            )
            success, total = ch.make_check("感知", 15)
            if success:
                self.narrate(f"你识破了幻术，检定 {total} >= 15，获得 1 点英雄灵感。")
                ch.inspiration += 1
            else:
                self.narrate(f"幻术太过逼真，检定 {total} < 15，你迷失一轮并增加疲劳。")
                ch.fatigue += 1

    def stage_forest_of_death(self) -> None:
        """死亡森林阶段，包含多日探索与生存。"""
        self.narrate(
            "阶段二：死亡森林\n"
            "你们进入了充满危机的死亡森林，在五天内必须收集天与地卷轴并到达终点塔。\n"
            "每一天，你们可以选择自己的行动，随机遭遇也会影响行程。"
        )
        # 初始化每个玩家拥有一个初始卷轴（随机天或地）
        for ch in self.players:
            initial_scroll = random.choice(["天", "地"])
            ch.scrolls.add(initial_scroll)
        # 五天循环
        while self.day <= 5:
            self.narrate(f"第 {self.day} 天冒险开始。")
            for ch in self.players:
                # 检查角色是否还活着
                if ch.hit_points <= 0:
                    self.narrate(f"{ch.name} 已经失去战斗能力，无法继续行动。")
                    continue
                # 如果已经收集到两个卷轴，可以选择直接前往终点
                if len(ch.scrolls) >= 2:
                    go_finish = self.prompt_choice(
                        f"{ch.name} 已经拥有天与地卷轴，你想要？", ["立即前往终点塔", "继续探索"],
                    )
                    if go_finish.startswith("立即"):
                        self.narrate(f"{ch.name} 决定直接前往终点塔，等待队友。")
                        continue
                # 行动选择
                action = self.prompt_choice(
                    f"{ch.name} 的行动选择：",
                    ["探索", "追踪", "埋伏", "休息", "交涉"],
                )
                if action == "休息":
                    ch.rest()
                    self.narrate(f"{ch.name} 选择休息，缓解疲劳，目前疲劳 {ch.fatigue}。")
                else:
                    # 触发随机事件
                    self.random_forest_event(ch)
            # 每天结束时疲劳检查
            for ch in self.players:
                if ch.hit_points > 0 and ch.fatigue > 0:
                    # 体质检定：难度随天数增加
                    success, total = ch.make_check("体质", 10 + self.day)
                    if not success:
                        ch.fatigue += 1
                        self.narrate(f"{ch.name} 因疲劳检定失败，疲劳增加至 {ch.fatigue}。")
            self.day += 1
        # 检查卷轴是否齐全
        for ch in self.players:
            if len(ch.scrolls) < 2 or ch.hit_points <= 0:
                ch.winner = False
        # 结束描述
        surviving = [p.name for p in self.players if p.winner]
        if surviving:
            self.narrate(
                f"恭喜 {'、'.join(surviving)} 成功离开死亡森林，进入下一阶段。"
            )
        else:
            self.narrate(
                "很遗憾，所有成员都未能完成卷轴收集或在途中倒下。冒险到此结束。"
            )

    def stage_preliminaries(self) -> None:
        """预赛阶段：一对一淘汰战。"""
        # 只有通过森林的角色才能参加预赛
        participants = [ch for ch in self.players if ch.winner and ch.hit_points > 0]
        if not participants:
            return
        self.narrate(
            "阶段三：预赛\n"
            "通过死亡森林的考生数量超出预期，因此将进行单人淘汰赛。"
        )
        for ch in participants:
            self.narrate(f"{ch.name} 的预赛对战开始……")
            wins = 0
            for round_no in range(1, 4):
                # 每回合对手难度略升
                dc = 14 + round_no
                success, total = ch.make_check("力量", dc)
                if success:
                    wins += 1
                    self.narrate(f"第 {round_no} 回合，你压制了对手，检定 {total} >= {dc}。")
                else:
                    self.narrate(f"第 {round_no} 回合，你未能占上风，检定 {total} < {dc}。")
                if wins >= 2:
                    break
            if wins >= 2:
                self.narrate(f"{ch.name} 获得了预赛胜利，进入决赛！")
                ch.winner = True
            else:
                self.narrate(f"{ch.name} 在预赛中落败，失去了晋级资格。")
                ch.winner = False

    def stage_finals(self) -> None:
        """决赛阶段：最终对决与木叶崩溃计划。"""
        finalists = [ch for ch in self.players if ch.winner and ch.hit_points > 0]
        if not finalists:
            return
        self.narrate(
            "阶段四：决赛及木叶崩溃计划\n"
            "在众多观众的注视下，你们将进行最终的中忍对决。然而，沙隐和音忍的阴谋也在暗处酝酿。"
        )
        for ch in finalists:
            # 感知检定察觉阴谋
            success, total = ch.make_check("感知", 14)
            if success:
                self.narrate(f"{ch.name} 察觉到异样，检定 {total} >= 14，预感到即将发生的袭击。")
                choice = self.prompt_choice(
                    "你如何选择？", ["报警并协助防御", "忽略预兆继续比赛"],
                )
                if choice.startswith("报警"):
                    # 协助防御需要力量或感知检定
                    success2, total2 = ch.make_check("力量", 15)
                    if success2:
                        self.narrate(f"{ch.name} 与上忍并肩作战，检定 {total2} >= 15，成功抵御了袭击！")
                        ch.winner = True
                    else:
                        self.narrate(f"{ch.name} 奋勇迎敌但仍受伤，检定 {total2} < 15，木叶遭受损失。")
                        ch.winner = False
                else:
                    # 继续比赛：决赛对手检定
                    success2, total2 = ch.make_check("力量", 16)
                    if success2:
                        self.narrate(f"{ch.name} 在决赛中大放异彩，检定 {total2} >= 16，赢得最终胜利！")
                        ch.winner = True
                    else:
                        self.narrate(f"{ch.name} 在决赛中落败，检定 {total2} < 16。")
                        ch.winner = False
            else:
                self.narrate(f"{ch.name} 没有察觉阴谋，检定 {total} < 14，只专注于比赛。")
                success2, total2 = ch.make_check("力量", 16)
                if success2:
                    self.narrate(f"你在决赛中获胜，检定 {total2} >= 16！")
                    ch.winner = True
                else:
                    self.narrate(f"你在决赛中落败，检定 {total2} < 16。")
                    ch.winner = False

    def conclude(self) -> None:
        """结束语，回顾成果。"""
        winners = [ch.name for ch in self.players if ch.winner and ch.hit_points > 0]
        if winners:
            self.narrate(
                f"恭喜 {'、'.join(winners)} 完成了中忍考试，晋升为中忍！\n感谢你们的努力，忍界的新篇章等待你们继续书写。"
            )
        else:
            self.narrate(
                "虽然未能成功，但失败也是成长的一部分。愿你们在下一次挑战中再创佳绩。"
            )

    def run(self) -> None:
        """按顺序运行所有阶段。"""
        self.stage_intro()
        self.stage_written_test()
        # 如果在笔试后没有人退出
        if any(ch.winner for ch in self.players):
            self.stage_forest_of_death()
            self.stage_preliminaries()
            self.stage_finals()
        self.conclude()


def main() -> None:
    print("欢迎体验火影·中忍考试文字冒险！")
    # 选择玩家数量
    while True:
        try:
            num = int(input("请输入玩家数量（1–3）: "))
            if 1 <= num <= 3:
                break
            print("数量必须在 1 到 3 之间。")
        except ValueError:
            print("请输入数字。")
    players: List[Character] = []
    for i in range(num):
        name = input(f"请输入玩家 {i + 1} 的名字: ")
        if not name:
            name = f"玩家{i + 1}"
        players.append(Character(name=name))
    dm = DM(players)
    dm.run()


if __name__ == "__main__":
    main()