import pywikibot
import openpyxl
import winsound
import os
import sys
from collections import defaultdict
from datetime import datetime
from pywikibot.tools import is_ip_address
from pywikibot.data.api import Request
from types import SimpleNamespace

I18N_DATA = {
    "en": {
        "editcount": "Edit count",
        "username": "Username",
        "rank": "Rank",
        "editsummary": "Bot: Update data",
        "pagetitle": "User:Wilf233/Editcount Ranking/data",
        "minimumeditcount" : "50",
    },
    "lzh": {
        "editcount": "纂次",
        "username": "簿名",
        "rank": "序第",
        "editsummary": "僕：新數更錄",
        "pagetitle": "使用者:Wilf233/纂次序第/數籍",
        "minimumeditcount" : "5",
    },
    "zh": {
        "editcount": "编辑数",
        "username": "用户名",
        "rank": "排名",
        "editsummary": "机器人：更新数据",
        "pagetitle": "User:Wilf233/编辑总数排名/数据",
        "minimumeditcount" : "30",
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
    site = pywikibot.Site(LANGUAGE, "mcw")
    site.login()
    base_dir = f'editcount-ranking-{LANGUAGE}-data'
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    output_dir = os.path.join(base_dir, timestamp)
    os.makedirs(output_dir, exist_ok=True)
    edit_counts = defaultdict(int)

    for rc in site.recentchanges(total=1):
        latest_revid = rc.get('revid')
    print(f"{get_time()} 检测到{LANGUAGE}全站共{latest_revid}条编辑")

    if site.has_right("apihighlimits"):
        batch_size = 500
        print(f"{get_time()} 检测到拥有apihighlimits权限")
    else:
        batch_size = 50
        print(f"{get_time()} 检测到没有apihighlimits权限")

    rev_count = 0

    for start in range(1, latest_revid + 1, batch_size):
        end = min(start + batch_size - 1, latest_revid)
        revids = list(range(start, end + 1))

        parameters = {
            'action': 'query',
            'prop': 'revisions',
            'revids':'|'.join(map(str, revids)),
            'rvprop': 'ids|user',
        }
        try:
            pages = Request(site=site, parameters=parameters).submit()['query']['pages']
        except:
            pass

        for page in pages.values():
            for rev in page.get('revisions', []):
                user = rev.get('user')
                if user:
                    edit_counts[user] += 1
                rev_count += 1
                if rev_count % 50000 == 0:
                    print(f"{get_time()} 已查找{rev_count}条编辑")

    print(f"{get_time()} 查找结束，共{rev_count}条编辑")

    sorted_results = sorted(edit_counts.items(), key=lambda x: x[1], reverse=True)

    ranked_results = []
    rank = 0
    prev_count = None
    for index, (user, count) in enumerate(sorted_results, start=1):
        if count != prev_count:
            rank = index
            prev_count = count
        ranked_results.append((rank, user, count))
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = datetime.now().strftime('%Y%m%d%H%M%S')
    ws.append([i18n.rank, i18n.username, i18n.editcount])
    wikitable = '{| class="wikitable sortable"\n'
    wikitable += f'! {i18n.rank} !! {i18n.username} !! {i18n.editcount}\n'
    for rank, user, count in ranked_results:
        ws.append([rank, user, count])
        if count >= int(i18n.minimumeditcount) and not is_ip_address(user):
            wikitable += f"|-\n| {rank} || [[User:{user}|]] || {count}\n"
    wb.save(os.path.join(output_dir, f"{LANGUAGE}minecraftwiki-editcount-ranking-{timestamp}.xlsx"))
    wikitable += "|}"
    with open(os.path.join(output_dir, f"{LANGUAGE}minecraftwiki-editcount-ranking-{timestamp}.txt"), "w", encoding="utf-8") as f:
        f.write(wikitable)
    print(f"{get_time()} 表格和文本均已生成")

    try:
        page = pywikibot.Page(site, i18n.pagetitle)
        page.text = wikitable
        page.save(i18n.editsummary)
    except Exception as e:
        print(f"{get_time()} {e}")

    winsound.MessageBeep()
    print(f"{get_time()} 运行结束")
    write_log(f"{get_time()} {__file__}完成运行\n")

if __name__ == "__main__":
    main()
