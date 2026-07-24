# ============================================================
# ikuuu 自动签到工具
# 功能：自动签到获取免费流量，并显示流量变化
# 使用：直接运行即可，无需任何操作
# ============================================================

import requests
import json
import re
import time
from urllib.parse import unquote
from datetime import datetime
from playwright.sync_api import sync_playwright
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ============================================================
# ⚙️ 配置区域（使用前请填写你的 Cookie）
# ============================================================

# 📌 从哪里获取 Cookie？
# 1. 用浏览器打开 https://ikuuu.win/user 并登录
# 2. 按 F12 打开开发者工具
# 3. 点击"网络"（Network）标签
# 4. 刷新页面（F5）
# 5. 点击第一个请求，在"请求标头"中找到 Cookie
# 6. 把下面的内容替换成你复制的 Cookie
# ============================================================

COOKIE_STRING = "替换成你复制的 Cookie"

SIGN_URL = "https://ikuuu.win/user/checkin"
USER_URL = "https://ikuuu.win/user"

# ⚠️ 注意：XPath 前面必须加 xpath= 前缀
TRAFFIC_XPATH = 'xpath=/html/body/div[2]/div/div[3]/section/div[3]/div[2]/div/div[2]/div[2]/span'


# ============================================================
# 以下代码不需要修改，直接运行即可
# ============================================================

def parse_cookie(cookie_string):
    """把 Cookie 字符串转成字典"""
    cookies = {}
    for item in cookie_string.split("; "):
        if "=" in item:
            key, value = item.split("=", 1)
            try:
                value = unquote(value)
            except:
                pass
            cookies[key] = value
    return cookies


def get_traffic():
    """获取当前剩余流量"""

    print("⏳ 正在查询当前流量...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # 注入 Cookie
            cookies = parse_cookie(COOKIE_STRING)
            for name, value in cookies.items():
                page.context.add_cookies([{
                    "name": name,
                    "value": value,
                    "domain": ".ikuuu.win",
                    "path": "/"
                }])

            page.goto(USER_URL, timeout=60000)
            page.wait_for_load_state("networkidle")
            time.sleep(5)

            # 用 XPath 定位流量元素（注意 xpath= 前缀）
            element = page.locator(TRAFFIC_XPATH)
            element.wait_for(timeout=10000)
            text = element.text_content()

            if text and text.strip():
                # 提取数字+单位
                match = re.search(r'(\d+\.?\d*)\s*(GB|MB|TB)', text)
                if match:
                    result = f"{match.group(1)} {match.group(2)}"
                    print(f"✅ 获取流量成功: {result}")
                    browser.close()
                    return result
                else:
                    print(f"✅ 获取流量成功: {text.strip()}")
                    browser.close()
                    return text.strip()
            else:
                print("❌ 获取到的流量为空")
                browser.close()
                return "查询失败"

    except Exception as e:
        print(f"⚠️ 查询流量时出错: {e}")
        return "查询失败"


def sign():
    """执行签到"""

    cookies = parse_cookie(COOKIE_STRING)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://ikuuu.win/user",
        "Origin": "https://ikuuu.win",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
    }

    session = requests.Session()
    session.cookies.update(cookies)

    try:
        response = session.post(SIGN_URL, headers=headers, timeout=30, verify=False)
        response.encoding = 'utf-8'

        result = {
            "success": False,
            "msg": "",
            "traffic": "",
        }

        try:
            data = response.json()
            result["msg"] = data.get("msg", "")

            flow_match = re.search(r'(\d+\.?\d*)\s*(MB|GB|KB)', result["msg"], re.IGNORECASE)
            if flow_match:
                result["traffic"] = f"{flow_match.group(1)} {flow_match.group(2)}"

            if data.get("ret") == 1:
                result["success"] = True
            elif "已签到" in result["msg"]:
                result["success"] = True
                result["msg"] = "今天已经签过到了"

        except:
            result["msg"] = response.text

        return result

    except Exception as e:
        return {
            "success": False,
            "msg": f"签到请求失败: {e}",
            "traffic": "",
        }


def main():
    """主程序"""

    # ===== 检查 Cookie 是否已配置 =====
    if COOKIE_STRING == "请替换为你的 Cookie 字符串":
        print("")
        print("╔" + "═" * 50 + "╗")
        print("║" + " " * 12 + "🌟 ikuuu 自动签到工具" + " " * 18 + "║")
        print("╚" + "═" * 50 + "╝")
        print("")
        print("❌ 错误：请先配置 Cookie！")
        print("")
        print("📖 获取 Cookie 的方法：")
        print("  1. 用浏览器打开 https://ikuuu.win/user 并登录")
        print("  2. 按 F12 打开开发者工具")
        print("  3. 点击「网络」标签")
        print("  4. 刷新页面（F5）")
        print("  5. 点击第一个请求，在「请求标头」中找到 Cookie")
        print("  6. 复制 Cookie 内容，粘贴到脚本的 COOKIE_STRING 变量中")
        print("")
        return

    # ===== 标题 =====
    print("")
    print("╔" + "═" * 50 + "╗")
    print("║" + " " * 12 + "🌟 ikuuu 自动签到工具" + " " * 18 + "║")
    print("╚" + "═" * 50 + "╝")
    print("")

    # ===== 开始时间 =====
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"📅 当前时间: {now}")
    print("")

    # ===== 第一步：获取签到前流量 =====
    print("─" * 50)
    print("📡 第一步：查询当前剩余流量")
    print("─" * 50)

    before = get_traffic()
    print(f"📦 当前剩余流量: {before}")
    print("")

    # ===== 第二步：执行签到 =====
    print("─" * 50)
    print("🎯 第二步：开始签到")
    print("─" * 50)

    print("⏳ 正在签到，请稍候...")
    result = sign()

    if result["success"]:
        print("✅ 签到成功！")
        if result["traffic"]:
            print(f"🎉 获得流量: {result['traffic']}")
        else:
            msg = result.get("msg", "")
            flow_match = re.search(r'(\d+\.?\d*)\s*(MB|GB|KB)', msg, re.IGNORECASE)
            if flow_match:
                print(f"🎉 获得流量: {flow_match.group(1)} {flow_match.group(2)}")
        print(f"📝 {result['msg']}")
    else:
        print(f"❌ 签到失败: {result['msg']}")
    print("")

    # ===== 第三步：获取签到后流量 =====
    print("─" * 50)
    print("📡 第三步：查询最新流量")
    print("─" * 50)

    print("⏳ 等待数据更新...")
    time.sleep(3)

    after = get_traffic()
    print(f"📦 最新剩余流量: {after}")
    print("")

    # ===== 汇总报告 =====
    print("─" * 50)
    print("📊 签到汇总")
    print("─" * 50)

    gained = result.get("traffic", "")
    if not gained:
        msg = result.get("msg", "")
        flow_match = re.search(r'(\d+\.?\d*)\s*(MB|GB|KB)', msg, re.IGNORECASE)
        if flow_match:
            gained = f"{flow_match.group(1)} {flow_match.group(2)}"

    if gained:
        print(f"  ✅ 本次获得流量: {gained}")

    print(f"  📈 签到前: {before}")
    print(f"  📈 签到后: {after}")

    if before != "查询失败" and after != "查询失败":
        try:
            bn = re.search(r'(\d+\.?\d*)', before)
            an = re.search(r'(\d+\.?\d*)', after)
            if bn and an:
                b = float(bn.group(1))
                a = float(an.group(1))
                diff = a - b
                bu = re.search(r'(GB|MB|TB)', before)
                au = re.search(r'(GB|MB|TB)', after)
                if bu and au and bu.group(1) == au.group(1):
                    if diff > 0:
                        print(f"  📊 净增长: +{diff:.2f} {bu.group(1)}")
                    elif diff < 0:
                        print(f"  📊 净变化: {diff:.2f} {bu.group(1)}")
        except:
            pass

    print("")
    print("╔" + "═" * 50 + "╗")
    print("║" + " " * 15 + "✅ 签到流程完成" + " " * 19 + "║")
    print("╚" + "═" * 50 + "╝")
    print("")


if __name__ == "__main__":
    main()
