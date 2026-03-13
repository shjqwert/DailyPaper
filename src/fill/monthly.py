"""每月月报自动填写"""
from playwright.sync_api import sync_playwright
from fill.base import login
import time

# TODO: 填入月报页面的 selector
SELECTORS = {
    "月份":     "",
    "项目":     "",
    "工作内容": "",
    "总工时":   "",
    "提交按钮": "",
}

MONTHLY_URL = ""  # TODO: 填入月报页面 URL



def run(cfg: dict, rows: list, start: str, end: str):
    if not cfg["intranet"]["username"]:
        print("错误: 请先在 config.json 中填写内网账号和密码")
        return
    required = ["工作内容", "总工时", "提交按钮"]
    missing = [k for k in required if not SELECTORS.get(k)]
    if missing:
        print(f"错误: fill/monthly.py 中以下 selector 未配置: {', '.join(missing)}")
        return

    # 按项目+节点汇总
    summary = {}
    for r in rows:
        key = (r["项目"], r["节点"])
        if key not in summary:
            summary[key] = {"工时": 0, "内容列表": []}
        summary[key]["工时"] += r["时间"]
        summary[key]["内容列表"].append(r["工作内容"])

    print(f"\n=== 本月汇总 [{start} ~ {end}] ===")
    total = 0
    for (proj, node), data in summary.items():
        print(f"  [{proj}] {node}: {data['工时']}h")
        total += data["工时"]
    print(f"  总计: {total}h")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        try:
            login(page, cfg, url=MONTHLY_URL or None)
        except RuntimeError as e:
            print(f"错误: {e}")
            browser.close()
            return

        try:
            for (proj, node), data in summary.items():
                content = "\n".join(data["内容列表"])
                # TODO: 根据实际月报页面结构调整
                if SELECTORS["项目"]:
                    page.select_option(SELECTORS["项目"], label=proj)
                if SELECTORS["工作内容"]:
                    page.fill(SELECTORS["工作内容"], content)
                if SELECTORS["总工时"]:
                    page.fill(SELECTORS["总工时"], str(data["工时"]))
                time.sleep(0.3)

            confirm = input(f"\n即将提交月报，确认? (y/n): ").strip()
            if confirm.lower() == "y":
                page.click(SELECTORS["提交按钮"])
                page.wait_for_load_state("networkidle")
                print("✓ 月报提交成功")
            else:
                input("已取消，按回车关闭浏览器...")
        except Exception as e:
            print(f"填写过程出错: {e}")
            input("按回车关闭浏览器...")
        finally:
            browser.close()
