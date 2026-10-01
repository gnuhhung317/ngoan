import json

def main():
    data = json.load(open('evaluated_jobs.json', encoding='utf-8'))
    tier_a = [j for j in data if j['tier'] == 'Tier A']
    top_15 = sorted(tier_a, key=lambda x: x['score'], reverse=True)[:15]

    with open('top_15_picks.md', 'w', encoding='utf-8') as f:
        for i, j in enumerate(top_15, 1):
            f.write(f"### TOP #{i} (Job #{j['index']}): [{j['title']}]({j['url']})\n")
            f.write(f"- **Công ty:** {j['company_name']}\n")
            f.write(f"- **Mức lương:** `{j['salary']}` | **Điểm phù hợp:** `{j['score']}/100` | **Nhóm:** `{j['role_category']}`\n")
            f.write(f"- **Kinh nghiệm:** {j['experience']} | **Địa điểm:** {j['locations']}\n")
            f.write("- **Ưu điểm:**\n")
            for p in j['pros']:
                f.write(f"  + {p}\n")
            if j['cons']:
                f.write("- **Lưu ý:**\n")
                for c in j['cons']:
                    f.write(f"  - {c}\n")
            f.write(f"- **Gợi ý CV:** *{j['cv_highlight']}*\n\n")
    print("Done writing top_15_picks.md")

if __name__ == "__main__":
    main()
