"""每周周报自动填写
周报字段可能与日报不同，回公司后同样需要配置 SELECTORS
"""
from playwright.sync_api import sync_playwright
from fill.base import login
import time

# TODO: 填入周报页面的 selector
SELECTORS = {
    "周期开始": "",
    "周期结束": "",
    "项目":     "",
    "工作内容": "",
    "总工时":   "",
    "提交按钮": "",
}

WEEKLY_URL = ""  # TODO: 填入周报页面 URL（如果与日报不同）



def run(cfg: dict, rows: list, start: str, end: str):
    if not cfg["intranet"]["username"]:
        print("错误: 请先在 config.json 中填写内网账号和密码")
        return
    required = ["工作内容", "总工时", "提交按钮"]
    missing = [k for k in required if not SELECTORS.get(k)]
    if missing:
        print(f"错误: fill/weekly.py 中以下 selector 未配置: {', '.join(missing)}")
        return

    # 按项目汇总
    summary = {}
    for r in rows:
        key = r["项目"]
        if key not in summary:
            summary[key] = {"工时": 0, "内容列表": []}
        summary[key]["工时"] += r["时间"]
        summary[key]["内容列表"].append(r["工作内容"])

    print(f"\n=== 本周汇总 [{start} ~ {end}] ===")
    for proj, data in summary.items():
        print(f"  {proj}: {data['工时']}h")
        for c in data["内容列表"]:
            print(f"    - {c}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        try:
            login(page, cfg, url=WEEKLY_URL or None)
        except RuntimeError as e:
            print(f"错误: {e}")
            browser.close()
            return

        try:
            for proj, data in summary.items():
                content = "\n".join(data["内容列表"])
                # TODO: 根据实际周报页面结构调整填写逻辑
                if SELECTORS["项目"]:
                    page.select_option(SELECTORS["项目"], label=proj)
                if SELECTORS["工作内容"]:
                    page.fill(SELECTORS["工作内容"], content)
                if SELECTORS["总工时"]:
                    page.fill(SELECTORS["总工时"], str(data["工时"]))
                time.sleep(0.3)

            confirm = input(f"\n即将提交周报，确认? (y/n): ").strip()
            if confirm.lower() == "y":
                page.click(SELECTORS["提交按钮"])
                page.wait_for_load_state("networkidle")
                print("✓ 周报提交成功")
            else:
                input("已取消，按回车关闭浏览器...")
        except Exception as e:
            print(f"填写过程出错: {e}")
            input("按回车关闭浏览器...")
        finally:
            browser.close()
