import pywikibot
import sys
from datetime import datetime, timezone, timedelta
from types import SimpleNamespace

I18N_DATA = {
    "en": {
        "editsummary": "Bot: Reset sandbox",
        "pagetitle": "Minecraft Wiki:Sandbox",
        "defaulttext": '''{{Sandbox heading}}
<!--
*               Welcome to the sandbox!              *
*            Please leave this part alone            *
*           The page is cleared regularly            *
*     Feel free to try your editing skills below     *
-->''',
    },
    "lzh": {
        "editsummary": "僕：清沙盤",
        "pagetitle": "Minecraft Wiki:沙盤",
        "defaulttext": '''{{Sandbox heading}}
<!-- 請纂於此註之下 -->''',
    },
    "zh": {
        "editsummary": "机器人：清空沙盒",
        "pagetitle": "Minecraft Wiki:沙盒",
        "defaulttext": '''{{Sandbox heading}}
<!-- 请在这段注释之后开始编辑，并请不要删除以上模板 -->''',
    },
}

def load_i18n(lang: str, fallback="en"):
    data = I18N_DATA.get(lang) or I18N_DATA[fallback]
    return SimpleNamespace(**data)

def get_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def write_log(text):
    with open("task.log", "a", encoding="utf-8") as f:
        f.write(text)

def main():
    LANGUAGE = sys.argv[1] if len(sys.argv) > 1 else input("请输入要运行的语言代码：")
    i18n = load_i18n(LANGUAGE)
    write_log(f"{get_time()} {__file__}开始运行，语言：{LANGUAGE}\n")
    site = pywikibot.Site(LANGUAGE, 'mcw')
    site.login()
    
    page = pywikibot.Page(site, i18n.pagetitle)
    last_edit = page.latest_revision.timestamp
    if last_edit.tzinfo is None:
        last_edit = last_edit.replace(tzinfo=timezone.utc)
    current_time = datetime.now(timezone.utc)
    if current_time - last_edit >= timedelta(hours=72):
        page.text = i18n.defaulttext
        page.save(i18n.editsummary)
        print(f"{get_time()} 已清空沙盒")
        write_log(f"{get_time()} {__file__}完成运行：已清空沙盒\n")
    else:
        print(f"{get_time()} 上一次编辑未满72小时")
        write_log(f"{get_time()} {__file__}完成运行：上一次编辑未满72小时\n")

if __name__ == "__main__":
    main()
