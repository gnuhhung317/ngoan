import json
import os
import re

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def analyze_batch(batch_idx):
    fname = f"batches/batch_{batch_idx:02d}.json"
    if not os.path.exists(fname):
        return None
    with open(fname, 'r', encoding='utf-8') as f:
        jobs = json.load(f)
    return jobs

def main():
    for b in range(1, 21):
        jobs = analyze_batch(b)
        if not jobs:
            continue
        print(f"=== BATCH {b:02d} ({len(jobs)} jobs) ===")
        for j in jobs:
            title = j['title']
            comp = j['company_name']
            sal = j['salary']
            exp = j['experience']
            print(f"[{j['index']}] {title} | {comp} | {sal} | {exp}")

if __name__ == "__main__":
    main()
