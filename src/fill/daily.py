"""每日日报自动填写
回公司后步骤：
1. 用浏览器打开内网日报页面
2. 按 F12 → Console，对每个字段右键 → Copy selector
3. 将 selector 填入下方 SELECTORS 字典
4. 运行 python report.py fill daily 测试
"""
from playwright.sync_api import sync_playwright
import time

# ============================================================
# TODO: 回公司后，将内网日报页面各字段的 CSS selector 填入此处
# 示例: "#date-input", "select[name='project']" 等
# ============================================================
SELECTORS = {
    "日期":     "",   # TODO
    "项目":     "",   # TODO
    "节点":     "",   # TODO
    "类型":     "",   # TODO
    "模块":     "",   # TODO
    "时间类型": "",   # TODO
    "时间":     "",   # TODO
    "工作内容": "",   # TODO
    "提交按钮": "",   # TODO
    "添加行按钮": "", # TODO (如果每行需要点"新增"按钮)
}


def login(page, cfg):
    page.goto(cfg["intranet"]["url"])
    # TODO: 根据实际登录页面调整 selector
    page.fill("input[name='username']", cfg["intranet"]["username"])
    page.fill("input[name='password']", cfg["intranet"]["password"])
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")


def fill_one_row(page, row: dict):
    """填写一行记录，根据实际页面结构调整"""
    # 点击"添加行"按钮（如果需要）
    if SELECTORS["添加行按钮"]:
        page.click(SELECTORS["添加行按钮"])
        time.sleep(0.5)

    if SELECTORS["日期"]:
        page.fill(SELECTORS["日期"], row["date"])
    if SELECTORS["项目"]:
        page.select_option(SELECTORS["项目"], label=row["项目"])
    if SELECTORS["节点"]:
        page.select_option(SELECTORS["节点"], label=row["节点"])
    if SELECTORS["类型"]:
        page.select_option(SELECTORS["类型"], label=row["类型"])
    if SELECTORS["模块"]:
        page.select_option(SELECTORS["模块"], label=row["模块"])
    if SELECTORS["时间类型"]:
        page.select_option(SELECTORS["时间类型"], label=row["时间类型"])
    if SELECTORS["时间"]:
        page.fill(SELECTORS["时间"], str(row["时间"]))
    if SELECTORS["工作内容"]:
        page.fill(SELECTORS["工作内容"], row["工作内容"])


def run(cfg: dict, rows: list):
    if not cfg["intranet"]["username"]:
        print("错误: 请先在 config.json 中填写内网账号和密码")
        return
    if not SELECTORS["工作内容"]:
        print("错误: 请先在 fill/daily.py 中配置字段 selector")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=False 方便调试
        page = browser.new_page()
        login(page, cfg)

        for row in rows:
            fill_one_row(page, row)
            time.sleep(0.3)

        # 提交
        if SELECTORS["提交按钮"]:
            confirm = input(f"\n即将提交 {len(rows)} 条记录，确认? (y/n): ").strip()
            if confirm.lower() == "y":
                page.click(SELECTORS["提交按钮"])
                page.wait_for_load_state("networkidle")
                print("✓ 日报提交成功")
            else:
                print("已取消，浏览器保持打开，可手动检查后提交")
                input("按回车关闭浏览器...")
        browser.close()
