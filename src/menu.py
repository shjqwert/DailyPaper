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
║    2. 补录历史日期记录             ║
╠══════════════════════════════════╣
║  【查看明细】                      ║
║    3. 今日记录                    ║
║    4. 本周记录                    ║
║    5. 本月记录                    ║
╠══════════════════════════════════╣
║  【工时统计（按项目）】             ║
║    6. 今日工时                    ║
║    7. 本周工时                    ║
║    8. 本月工时                    ║
║    9. 指定月份工时                 ║
╠══════════════════════════════════╣
║  【加班统计】                      ║
║   10. 本周加班                    ║
║   11. 本月加班                    ║
╠══════════════════════════════════╣
║  【自动填报】                      ║
║   12. 填写今日日报                 ║
║   13. 填写本周周报                 ║
║   14. 填写本月月报                 ║
╠══════════════════════════════════╣
║    0. 退出                        ║
╚══════════════════════════════════╝
"""

def add_past():
    from datetime import datetime, date
    while True:
        raw = input("\n请输入日期 (格式 YYYY-MM-DD，如 2026-03-01，q 取消): ").strip()
        if raw.lower() == "q":
            raise report.GoBack
        try:
            d = datetime.strptime(raw, "%Y-%m-%d").date()
            if d > date.today():
                print("  不能补录未来日期，请重试")
                continue
            return raw
        except ValueError:
            print("  格式错误，请重试")


ACTIONS = {
    "1":  ("添加今日记录",      lambda cfg: report.cmd_add(cfg)),
    "2":  ("补录历史日期记录",  lambda cfg: report.cmd_add(cfg, add_past())),
    "3":  ("今日明细",          lambda cfg: report.cmd_show("day")),
    "4":  ("本周明细",          lambda cfg: report.cmd_show("week")),
    "5":  ("本月明细",          lambda cfg: report.cmd_show("month")),
    "6":  ("今日工时统计",      lambda cfg: report.cmd_hours("day")),
    "7":  ("本周工时统计",      lambda cfg: report.cmd_hours("week")),
    "8":  ("本月工时统计",      lambda cfg: report.cmd_hours("month")),
    "9":  ("指定月份工时统计",  lambda cfg: report.cmd_hours_by_month()),
    "10": ("本周加班统计",      lambda cfg: report.cmd_overtime("week", cfg)),
    "11": ("本月加班统计",      lambda cfg: report.cmd_overtime("month", cfg)),
    "12": ("填写今日日报",      lambda cfg: report.cmd_fill("daily", cfg)),
    "13": ("填写本周周报",      lambda cfg: report.cmd_fill("weekly", cfg)),
    "14": ("填写本月月报",      lambda cfg: report.cmd_fill("monthly", cfg)),
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
            try:
                action(cfg)
            except report.GoBack:
                print("\n  已取消，返回菜单")
            input("\n按回车返回菜单...")
        else:
            print("无效输入，请重试")


if __name__ == "__main__":
    main()
