import pywikibot
import pandas as pd
import winsound
import os
from datetime import datetime

def get_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def write_log(text):
    with open("task.log", "a", encoding="utf-8") as f:
        f.write(text)

def main():
    write_log(f"{get_time()} {__file__} 开始运行\n")
    print(f"{get_time()} 开始运行")
    site = pywikibot.Site('en', 'mcw')
    site.login()
    base_dir = 'global-editcount-ranking-data'
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    output_dir = os.path.join(base_dir, timestamp)
    os.makedirs(output_dir, exist_ok=True)

    users = []
    count = 0
    parameters = {
        'action': 'query',
        'list': 'allusers',
        'auprop':'editcount',
        'aulimit': 5000
    }
    request = pywikibot.data.api.ListGenerator('allusers', site=site, parameters=parameters)
    for user in request:
        users.append({
            'Name': user.get('name'),
            'EditCount': user.get('editcount', 0),
        })
        count += 1
        if count % 5000 == 0:
            print(f"{get_time()} 已查找{count}个用户")
    print(f"{get_time()} 查找完毕，共{count}个用户")

    df = pd.DataFrame(users)
    df = df.sort_values(by='EditCount', ascending=False).reset_index(drop=True)
    df['Rank'] = df['EditCount'].rank(method='min', ascending=False).astype(int)
    df = df[['Rank', 'Name', 'EditCount']]
    df.to_excel(os.path.join(output_dir, f'MCWiki-global-editcount-ranking-{timestamp}.xlsx'), index=False)
    print(f"{get_time()} 表格已生成")

    wikitable_lines = []
    wikitable_lines.append('{| class="wikitable sortable"')
    wikitable_lines.append('! Rank !! User name !! Edit count')
    df = df[df['EditCount'] >= 50]

    for _, row in df.iterrows():
        wikitable_lines.append(
            f'|-\n| {row["Rank"]} || [[User:{row["Name"]}|]] || {row["EditCount"]}'
        )

    wikitable_lines.append('|}')
    wikitable_text = '\n'.join(wikitable_lines)

    with open(os.path.join(output_dir, f'MCWiki-global-editcount-ranking-{timestamp}.txt'), 'w', encoding='utf-8') as f:
        f.write(wikitable_text)
    print(f"{get_time()} 文本已生成")

    try:
        page_title = 'User:Wilf233/Global Editcount Ranking/data'
        page = pywikibot.Page(site, page_title)
        page.text = wikitable_text
        page.save("Bot: Update data")
    except Exception as e:
        print(get_time() + e)

    winsound.MessageBeep()
    print(f"{get_time()} 运行结束")
    write_log(f"{get_time()} {__file__} 完成运行\n")

if __name__ == "__main__":
    main()
