"""Command-line entrypoint for the text adventure."""

import argparse

from .dm import run_game


def main() -> None:
    parser = argparse.ArgumentParser(description="火影忍者：中忍考试篇（文字版）")
    parser.add_argument("--seed", type=int, default=None, help="随机种子，便于复现跑团流程")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="使用默认角色与脚本选择自动演示一遍流程（非交互）",
    )
    args = parser.parse_args()

    scripted = ["新晋忍者", "t", "k"] if args.demo else None
    run_game(seed=args.seed, scripted_choices=scripted, demo_mode=args.demo)


if __name__ == "__main__":
    main()
