#!/usr/bin/env python3
"""日报填写助手 - 主入口
用法:
  python report.py add            # 添加今日工作记录
  python report.py show           # 查看今日记录
  python report.py show week      # 查看本周记录
  python report.py show month     # 查看本月记录
  python report.py hours          # 按项目统计今日工时
  python report.py hours week     # 按项目统计本周工时
  python report.py hours month    # 按项目统计本月工时
  python report.py delete <id>    # 删除一条记录
  python report.py fill daily     # 自动填写今日日报（需配置内网）
  python report.py fill weekly    # 自动填写本周周报（需配置内网）
  python report.py fill monthly   # 自动填写本月月报（需配置内网）
"""
import sys
import json
from datetime import date
from pathlib import Path
import db

CONFIG_PATH = Path(__file__).parent.parent / "config.json"


def load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def pick(prompt, options, allow_custom=False, cfg=None, field_key=None):
    """数字快速选择，手动输入的新值自动保存到 config.json"""
    print(f"\n{prompt}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    if allow_custom:
        print(f"  0. 手动输入")
    while True:
        raw = input("请选择编号: ").strip()
        if allow_custom and raw == "0":
            value = input("请输入: ").strip()
            if cfg and field_key and value not in cfg["options"][field_key]:
                cfg["options"][field_key].append(value)
                save_config(cfg)
                print(f"  ✓ 已保存至选项列表")
            return value
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        print("  输入无效，请重试")


def cmd_add(cfg, date_str=None):
    if date_str is None:
        date_str = date.today().isoformat()
    opts = cfg["options"]

    print(f"\n=== 添加工作记录 [{date_str}] ===")

    项目 = pick("【项目】", opts["项目"], allow_custom=True, cfg=cfg, field_key="项目")
    节点 = pick("【节点】", opts["节点"], allow_custom=True, cfg=cfg, field_key="节点")
    类型 = pick("【类型】", opts["类型"], allow_custom=True, cfg=cfg, field_key="类型")
    模块 = pick("【模块】", opts["模块"], allow_custom=True, cfg=cfg, field_key="模块")
    时间类型 = pick("【时间类型】", opts["时间类型"])

    while True:
        raw = input("\n【工时(小时)】请输入(如 2 或 1.5): ").strip()
        try:
            时间 = float(raw)
            break
        except ValueError:
            print("  请输入数字")

    工作内容 = input("\n【工作内容】请简要描述: ").strip()

    db.add_log(date_str, 项目, 节点, 类型, 模块, 时间类型, 时间, 工作内容)

    print(f"\n✓ 已保存: [{项目}] {模块} - {工作内容} ({时间}h)")

    again = input("\n继续添加? (y/n, 默认n): ").strip().lower()
    if again == "y":
        cmd_add(cfg, date_str)


def fmt_rows(rows):
    if not rows:
        print("  (暂无记录)")
        return
    total = 0
    for r in rows:
        print(f"  [{r['id']}] {r['date']} | {r['项目']} | {r['节点']} | "
              f"{r['类型']} | {r['模块']} | {r['时间类型']} | "
              f"{r['时间']}h | {r['工作内容']}")
        total += r['时间']
    print(f"\n  合计工时: {total}h")


def cmd_hours(scope="day"):
    if scope == "day":
        today = date.today().isoformat()
        rows = db.query_by_date(today)
        label = f"今日 [{today}]"
    elif scope == "week":
        start, end = db.get_week_range()
        rows = db.query_by_range(start, end)
        label = f"本周 [{start} ~ {end}]"
    elif scope == "month":
        start, end = db.get_month_range()
        rows = db.query_by_range(start, end)
        label = f"本月 [{start} ~ {end}]"
    else:
        print("用法: python report.py hours [week|month]")
        return

    if not rows:
        print("  (暂无记录)")
        return

    # 按项目汇总
    summary = {}
    total = 0
    for r in rows:
        proj = r["项目"]
        summary.setdefault(proj, {"工时": 0, "明细": []})
        summary[proj]["工时"] += r["时间"]
        summary[proj]["明细"].append(f"{r['date']} {r['模块']} {r['工作内容']} ({r['时间']}h)")
        total += r["时间"]

    print(f"\n=== 按项目工时统计 {label} ===")
    bar_max = 20
    max_h = max(v["工时"] for v in summary.values()) or 1
    for proj, data in sorted(summary.items(), key=lambda x: -x[1]["工时"]):
        bar_len = int(data["工时"] / max_h * bar_max)
        bar = "█" * bar_len
        pct = data["工时"] / total * 100
        print(f"\n  {proj}")
        print(f"    {bar} {data['工时']}h ({pct:.1f}%)")
        for item in data["明细"]:
            print(f"      · {item}")
    print(f"\n  总计: {total}h")


def cmd_hours_by_month(month_str=None):
    """按指定月份统计工时，month_str 格式 YYYY-MM，不传则交互输入"""
    if not month_str:
        month_str = input("\n请输入月份 (格式 YYYY-MM，如 2026-02): ").strip()
    try:
        year, month = int(month_str[:4]), int(month_str[5:7])
    except (ValueError, IndexError):
        print("  格式错误，请输入如 2026-02")
        return
    from datetime import date as _date
    import calendar
    start = f"{year}-{month:02d}-01"
    last_day = calendar.monthrange(year, month)[1]
    end = f"{year}-{month:02d}-{last_day:02d}"
    rows = db.query_by_range(start, end)
    label = f"{year}年{month:02d}月 [{start} ~ {end}]"

    if not rows:
        print(f"  {label} 暂无记录")
        return

    summary = {}
    total = 0
    for r in rows:
        proj = r["项目"]
        summary.setdefault(proj, {"工时": 0, "明细": []})
        summary[proj]["工时"] += r["时间"]
        summary[proj]["明细"].append(f"{r['date']} {r['模块']} {r['工作内容']} ({r['时间']}h)")
        total += r["时间"]

    print(f"\n=== 按项目工时统计 {label} ===")
    bar_max = 20
    max_h = max(v["工时"] for v in summary.values()) or 1
    for proj, data in sorted(summary.items(), key=lambda x: -x[1]["工时"]):
        bar_len = int(data["工时"] / max_h * bar_max)
        bar = "█" * bar_len
        pct = data["工时"] / total * 100
        print(f"\n  {proj}")
        print(f"    {bar} {data['工时']}h ({pct:.1f}%)")
        for item in data["明细"]:
            print(f"      · {item}")
    print(f"\n  总计: {total}h")


def cmd_show(scope="day"):
    if scope == "day":
        today = date.today().isoformat()
        print(f"\n=== 今日记录 [{today}] ===")
        fmt_rows(db.query_by_date(today))
    elif scope == "week":
        start, end = db.get_week_range()
        print(f"\n=== 本周记录 [{start} ~ {end}] ===")
        fmt_rows(db.query_by_range(start, end))
    elif scope == "month":
        start, end = db.get_month_range()
        print(f"\n=== 本月记录 [{start} ~ {end}] ===")
        fmt_rows(db.query_by_range(start, end))


def cmd_delete(log_id):
    db.delete_log(int(log_id))
    print(f"✓ 已删除记录 id={log_id}")


def cmd_fill(scope, cfg):
    try:
        from fill import daily, weekly, monthly
    except ImportError:
        print("错误: 缺少 fill 模块，请确认 fill/ 目录存在")
        return

    if scope == "daily":
        today = date.today().isoformat()
        rows = db.query_by_date(today)
        if not rows:
            print("今日暂无记录，请先 python report.py add")
            return
        daily.run(cfg, [dict(r) for r in rows])
    elif scope == "weekly":
        start, end = db.get_week_range()
        rows = db.query_by_range(start, end)
        weekly.run(cfg, [dict(r) for r in rows], start, end)
    elif scope == "monthly":
        start, end = db.get_month_range()
        rows = db.query_by_range(start, end)
        monthly.run(cfg, [dict(r) for r in rows], start, end)


def main():
    db.init_db()
    cfg = load_config()

    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return

    cmd = args[0]

    if cmd == "add":
        date_str = args[1] if len(args) > 1 else None
        cmd_add(cfg, date_str)
    elif cmd == "show":
        scope = args[1] if len(args) > 1 else "day"
        cmd_show(scope)
    elif cmd == "hours":
        scope = args[1] if len(args) > 1 else "day"
        cmd_hours(scope)
    elif cmd == "delete" and len(args) > 1:
        cmd_delete(args[1])
    elif cmd == "fill" and len(args) > 1:
        cmd_fill(args[1], cfg)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
