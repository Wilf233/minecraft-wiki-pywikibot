import pywikibot
import winsound
import sys
import json
from datetime import datetime
from types import SimpleNamespace
from pywikibot.data.api import Request

I18N_DATA = {
    "en": {
        "editsummary": "Bot: Update data",
        "pagetitle":"Module:Group rights/data.json",
    },
    "lzh": {
        "editsummary": "僕：新數更錄",
    },
    "uk": {
        "editsummary": "Бот: Оновити дані",
        "pagetitle":"Модуль:Права групи/data.json",
    },
    "zh": {
        "editsummary": "机器人：更新数据",
        "pagetitle":"Module:Group rights/data.json",
    },
    "meta": {
        "editsummary": "Bot: Update data",
        "pagetitle":"Module:Group rights/data.json",
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

def fetch_usergroups(site: pywikibot.Site) -> dict:
    req = Request(
        site=site,
        parameters={
            "action": "query",
            "meta": "siteinfo",
            "siprop": "usergroups",
            "format": "json",
            "formatversion": 2,
        },
    )
    return req.submit()

def pretty_print_json(data: dict) -> str:
    return json.dumps(
        data,
        indent=2,
        ensure_ascii=False,
        #sort_keys=True,
    )

def main():
    LANGUAGE = sys.argv[1] if len(sys.argv) > 1 else input("请输入要运行的语言代码：")
    i18n = load_i18n(LANGUAGE)
    write_log(f"{get_time()} {__file__}开始运行，语言：{LANGUAGE}\n")
    site = pywikibot.Site(LANGUAGE, "mcw")
    site.login()
    api_data = fetch_usergroups(site)
    api_data["query"].pop("userinfo", None)
    pretty_json = pretty_print_json(api_data)
    try:
        page = pywikibot.Page(site, i18n.pagetitle)
        if not page.exists():
            print(f"{page.title}页面不存在！")
            exit()
        page.text = pretty_json
        page.save(i18n.editsummary, minor = False, bot = False)
    except Exception as e:
        print(get_time() + e)

    winsound.MessageBeep()
    print(f"{get_time()} 运行结束")
    write_log(f"{get_time()} {__file__}完成运行\n")

if __name__ == "__main__":
    main()
