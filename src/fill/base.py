"""fill 模块公共函数"""


def login(page, cfg, url=None):
    """登录内网，登录后验证是否成功（URL 应发生跳转）"""
    target_url = url or cfg["intranet"]["url"]
    if not target_url or target_url == "http://your-intranet-url":
        raise RuntimeError("请先在 config.json 中填写正确的内网地址")
    page.goto(target_url, timeout=30000)
    page.fill("input[name='username']", cfg["intranet"]["username"])
    page.fill("input[name='password']", cfg["intranet"]["password"])
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle", timeout=30000)

    # 验证登录：若 URL 未变化（仍在登录页），说明登录失败
    if page.url == target_url:
        raise RuntimeError("登录失败，请检查用户名和密码是否正确")
