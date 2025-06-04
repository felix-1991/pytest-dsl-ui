import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("chrome-error://chromewebdata/")
    page.get_by_role("button", name="高级").click()
    page.get_by_role("link", name="继续前往10.65.173.36（不安全）").click()
    page.get_by_role("textbox", name="请输入您的用户名").click()
    page.get_by_role("textbox", name="请输入您的用户名").fill("admin")
    page.get_by_role("textbox", name="请输入您的用户名").press("Tab")
    page.get_by_role("textbox", name="请输入您的密码").fill("admin")
    page.get_by_role("textbox", name="请输入您的密码").press("Tab")
    page.get_by_role("textbox", name="请按右图输入验证码").fill("qhz8")
    page.get_by_role("checkbox", name="我已阅读并同意").check()
    page.get_by_role("button", name="立即登录").click()
    page.get_by_role("button", name="以后再说").click()
    page.get_by_label("日志检索", exact=True).locator("div").filter(has_text="日志检索").click()
    page.get_by_role("button", name="简易模式 down").click()
    page.get_by_text("专家模式", exact=True).click()
    page.get_by_role("textbox", name="请选择访问方向").click()
    page.get_by_text("外到内").click()
    page.get_by_role("cell", name="外到内").locator("label").first.click()
    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
