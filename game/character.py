"""Character representation and helper utilities."""

from dataclasses import dataclass, field
from typing import Dict, List

from .dice import ability_modifier


AbilityScores = Dict[str, int]


STANDARD_ARRAY = [16, 14, 13, 12, 10, 8]
BACKGROUND_BONUSES = {
    "木叶村天赋": {"体魄": 2, "感知": 1, "inspiration_on_long_rest": True},
    "砂隐之村训练": {"体术": 2, "知识": 1},
    "音忍村研究": {"知识": 2, "意志": 1},
}
ARCHETYPE_PRIORITIES = {
    "体术专家": ["体术", "速度", "体魄", "感知", "意志", "知识"],
    "忍术专家": ["知识", "意志", "体魄", "速度", "感知", "体术"],
    "幻术/医疗专家": ["意志", "感知", "知识", "体魄", "速度", "体术"],
}


@dataclass
class Character:
    """Simple player character sheet used by the automated DM."""

    name: str
    archetype: str
    background: str
    ability_scores: AbilityScores
    proficiency: int = 2
    hero_inspiration: bool = False
    hp: int = 0
    chakra: int = 0
    fatigue: int = 0
    scrolls: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.hp:
            self.hp = 8 + self.modifier("体魄")
        if not self.chakra:
            self.chakra = self.ability_scores.get("体魄", 10) + self.ability_scores.get("意志", 10) * 2

    def modifier(self, key: str) -> int:
        return ability_modifier(self.ability_scores.get(key, 10))

    def adjust_hp(self, amount: int) -> None:
        self.hp = max(0, self.hp + amount)

    def spend_chakra(self, amount: int) -> bool:
        if self.chakra < amount:
            return False
        self.chakra -= amount
        return True

    def gain_fatigue(self, amount: int = 1) -> None:
        self.fatigue = max(0, self.fatigue + amount)

    def rest(self, full: bool = False) -> None:
        if full:
            self.hp = max(self.hp, 8 + self.modifier("体魄"))
            self.chakra = self.ability_scores.get("体魄", 10) + self.ability_scores.get("意志", 10) * 2
            if BACKGROUND_BONUSES.get(self.background, {}).get("inspiration_on_long_rest"):
                self.hero_inspiration = True
        else:
            recovered = max(1, self.modifier("体魄"))
            self.hp += recovered
            self.chakra = min(self.chakra + recovered, self.ability_scores.get("体魄", 10) + self.ability_scores.get("意志", 10) * 2)
        if self.fatigue:
            self.fatigue -= 1


def build_ability_scores(archetype: str, background: str) -> AbilityScores:
    ordered_stats = ARCHETYPE_PRIORITIES[archetype]
    base = dict(zip(ordered_stats, STANDARD_ARRAY))
    for ability in ["体术", "速度", "体魄", "知识", "感知", "意志"]:
        base.setdefault(ability, 10)
    bonuses = BACKGROUND_BONUSES.get(background, {})
    for ability, bonus in bonuses.items():
        if ability.endswith("rest"):
            continue
        base[ability] = base.get(ability, 10) + bonus
    return base
