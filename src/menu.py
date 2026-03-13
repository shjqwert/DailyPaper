#!/usr/bin/env python3
"""日报助手 - 交互菜单"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import db
import report

MENU = """
╔══════════════════════════════════╗
║         日报填写助手              ║
╠══════════════════════════════════╣
║  【录入】                         ║
║    1. 添加今日工作记录             ║
╠══════════════════════════════════╣
║  【查看明细】                      ║
║    2. 今日记录                    ║
║    3. 本周记录                    ║
║    4. 本月记录                    ║
╠══════════════════════════════════╣
║  【工时统计（按项目）】             ║
║    5. 今日工时                    ║
║    6. 本周工时                    ║
║    7. 本月工时                    ║
╠══════════════════════════════════╣
║  【自动填报】                      ║
║    8. 填写今日日报                 ║
║    9. 填写本周周报                 ║
║   10. 填写本月月报                 ║
╠══════════════════════════════════╣
║    0. 退出                        ║
╚══════════════════════════════════╝
"""

ACTIONS = {
    "1":  ("添加今日记录",   lambda cfg: report.cmd_add(cfg)),
    "2":  ("今日明细",       lambda cfg: report.cmd_show("day")),
    "3":  ("本周明细",       lambda cfg: report.cmd_show("week")),
    "4":  ("本月明细",       lambda cfg: report.cmd_show("month")),
    "5":  ("今日工时统计",   lambda cfg: report.cmd_hours("day")),
    "6":  ("本周工时统计",   lambda cfg: report.cmd_hours("week")),
    "7":  ("本月工时统计",   lambda cfg: report.cmd_hours("month")),
    "8":  ("填写今日日报",   lambda cfg: report.cmd_fill("daily", cfg)),
    "9":  ("填写本周周报",   lambda cfg: report.cmd_fill("weekly", cfg)),
    "10": ("填写本月月报",   lambda cfg: report.cmd_fill("monthly", cfg)),
}


def main():
    db.init_db()
    cfg = report.load_config()

    while True:
        print(MENU)
        choice = input("请输入编号: ").strip()

        if choice == "0":
            print("再见！")
            break
        elif choice in ACTIONS:
            name, action = ACTIONS[choice]
            print(f"\n>>> {name}")
            action(cfg)
            input("\n按回车返回菜单...")
        else:
            print("无效输入，请重试")


if __name__ == "__main__":
    main()
