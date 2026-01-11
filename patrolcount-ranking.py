import pywikibot
import openpyxl
import winsound
import os
import sys
from collections import defaultdict
from datetime import datetime
from types import SimpleNamespace

I18N_DATA = {
    "en": {
        "patrolcount": "Patrol count",
        "username": "Username",
        "rank": "Rank",
        "editsummary": "Bot: Update data",
        "pagetitle": "User:Wilf233/Patrolcount Ranking/data",
    },
    "lzh": {
        "patrolcount": "哨次",
        "username": "簿名",
        "rank": "序第",
        "editsummary": "僕：新數更錄",
        "pagetitle": "使用者:Wilf233/哨次序第/數籍",
    },
    "zh": {
        "patrolcount": "巡查数",
        "username": "用户名",
        "rank": "排名",
        "editsummary": "机器人：更新数据",
        "pagetitle": "User:Wilf233/巡查总数排名/数据",
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
    base_dir = f'patrolcount-ranking-{LANGUAGE}-data'
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    output_dir = os.path.join(base_dir, timestamp)
    os.makedirs(output_dir, exist_ok=True)

    patrol_counts = defaultdict(int)
    n = 0
    for logevent in site.logevents(logtype='patrol'):
        if logevent.user and not('auto' in logevent.params):
            username = str(logevent.user())
            patrol_counts[username] += 1
            n += 1
        if n % 50000 == 0:
            print(f"{get_time()} 已查找{n}条日志")
    print(f"{get_time()} 查找完毕，共{n}条日志")

    sorted_results = sorted(patrol_counts.items(), key=lambda x: x[1], reverse=True)
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
    ws.append([i18n.rank, i18n.username, i18n.patrolcount])
    wikitable = '{| class="wikitable sortable"\n'
    wikitable += f"! {i18n.rank} !! {i18n.username} !! {i18n.patrolcount}\n"
    for rank, user, count in ranked_results:
        ws.append([rank, user, count])
        wikitable += f"|-\n| {rank} || [[User:{user}|]] || {count}\n"
    wb.save(os.path.join(output_dir, f"{LANGUAGE}minecraftwiki-patrolcount-ranking-{timestamp}.xlsx"))
    wikitable += "|}"
    with open(os.path.join(output_dir, f"{LANGUAGE}minecraftwiki-patrolcount-ranking-{timestamp}.txt"), "w", encoding="utf-8") as f:
        f.write(wikitable)
    print(f"{get_time()} 表格和文本已生成")

    try:
        page = pywikibot.Page(site, i18n.pagetitle)
        page.text = wikitable
        page.save(i18n.editsummary)
    except Exception as e:
        print(get_time() + e)

    winsound.MessageBeep()
    print(f"{get_time()} 运行结束")
    write_log(f"{get_time()} {__file__}完成运行\n")

if __name__ == "__main__":
    main()
