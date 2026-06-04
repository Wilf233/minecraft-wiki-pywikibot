import pywikibot
import winsound
import pandas as pd
from pywikibot.data.api import Request
from datetime import datetime
from types import SimpleNamespace
from html.parser import HTMLParser

I18N_DATA = {
    "de": {
        "prefix": "",
        "suffix": "+ Artikel",
    },
    "en": {
        "prefix": "",
        "suffix": "+ articles",
    },
    "es": {
        "prefix": "",
        "suffix": "+ artículos",
    },
    "fr": {
        "prefix": "",
        "suffix": "+ articles",
    },
    "it": {
        "prefix": "",
        "suffix": "+ articoli",
    },
    "ja": {
        "prefix": "",
        "suffix": "本以上の記事",
    },
    "ko": {
        "prefix": "문서 ",
        "suffix": "개 이상",
    },
    "lzh": {
        "prefix": "",
        "suffix": "餘文",
    },
    "nl": {
        "prefix": "",
        "suffix": "+ artikels",
    },
    "pt-br": {
        "prefix": "+",
        "suffix": " artigos",
    },
    "ru": {
        "prefix": "",
        "suffix": "+ статей",
    },
    "th": {
        "prefix": "",
        "suffix": "+ หน้า",
    },
    "uk": {
        "prefix": "",
        "suffix": "+ статей",
    },
    "zh": {
        "prefix": "",
        "suffix": "+ 条目 / 條目",
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

def language_code_to_name(lang):
    html = Request(
        site=pywikibot.Site(lang, "mcw"),
        parameters={
            "action": "parse",
            "text": "{{#language:%s}}" % lang,
            "contentmodel": "wikitext",
            "prop": "text",
        }
    ).submit()["parse"]["text"]["*"]

    p = HTMLParser()
    buf = []
    p.handle_data = buf.append
    p.feed(html)
    return "".join(buf).strip()

def get_article_number(lang):
    stats = Request(
        site = pywikibot.Site(lang, "mcw"),
        parameters={
            'action': 'query',
            'meta': 'siteinfo',
            'siprop': 'statistics',
        }
    ).submit()['query']['statistics']

    return stats.get('articles')

def format_number(num, lang):
    num = num // 100 * 100
    num = f"{num:,}"
    lang = lang.lower().split("-")[0]
    if lang in {"de"}:
        num = num.replace(",", ".")
    elif lang in {"fr", "pt", "pt-br", "ru"}:
        num = num.replace(",", " ")
    return num

def capitalize_first_char(s):
    if not s:
        return s
    return s[0].upper() + s[1:]

def main():
    write_log(f"{get_time()} {__file__}开始运行\n")
    site = pywikibot.Site("meta", "mcw")
    page = pywikibot.Page(site, 'Languages')
    '''
    if page.latest_revision.user != "Wilfbot":
        if input("最后一次编辑不是Wilfbot完成的，继续请输入Y：") != "Y":
            write_log(f"{get_time()} {__file__}上一次编辑不是Wilfbot\n")
            exit()
    '''
    language_list = site.codes
    language_list -= {"meta", "pt"}
    data = []
    count = 0
    for lang in language_list:
        i18n = load_i18n(lang)
        data_site = pywikibot.Site(lang, "mcw")
        data.append({
            'Lang': lang,
            'MainPageName': data_site.mediawiki_message('mainpage'),
            'LanguageName': capitalize_first_char(language_code_to_name(lang)),
            'ArticleNumber': get_article_number(lang),
            'Prefix': i18n.prefix,
            'Suffix': i18n.suffix
        })
        count += 1
        print(f"{get_time()} 已查找{count}个语言")

    df = pd.DataFrame(data)
    df = df.sort_values(by='ArticleNumber', ascending=False).reset_index(drop=True)
    text = '''<templatestyles src=":Languages/styles.css" /><div id="lang-select">

[[File:Wiki@2x textless.png|x240px|link=]][[File:Minecraft_Wiki_default_header.svg|x160px|link=]]

<div class="lang-btns">\n'''
    for _, row in df.iterrows():
        text += f'<div class="lang-btn">[[{row["Lang"].split("-")[0]}:{row["MainPageName"]}|<div>\'\'\'{row["LanguageName"]}\'\'\'<br><span>{row["Prefix"]}{format_number(row["ArticleNumber"], row["Lang"])}{row["Suffix"]}</span></div>]]</div>\n'

    text += '''<div class="lang-btn">[[Main Page|<div>\'\'\'Meta Wiki\'\'\'<br><span>{{NUMBEROFARTICLES}} articles</span></div>]]</div>
</div>

</div>

[[Category:Community]]'''
    try:
        page.text = text
        print(text)
        page.save("Bot: Update data")
    except Exception as e:
        print(get_time() + e)
    
    winsound.MessageBeep()
    print(f"{get_time()} 运行结束")
    write_log(f"{get_time()} {__file__}完成运行\n")

if __name__ == "__main__":
    main()
