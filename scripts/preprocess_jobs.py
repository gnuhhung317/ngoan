import json
import re
import html
from pathlib import Path

def clean_html(raw_html):
    if not raw_html or not isinstance(raw_html, str):
        return ""
    # Replace breaks and list items with newline
    text = re.sub(r'<(?:br|p|li|div|h[1-6])[\s/>]', '\n', raw_html, flags=re.IGNORECASE)
    # Remove remaining tags
    text = re.sub(r'<[^>]+>', '', text)
    # Unescape HTML entities
    text = html.unescape(text)
    # Normalize multiple newlines and spaces
    lines = [line.strip() for line in text.splitlines()]
    clean_lines = [l for l in lines if l]
    return "\n".join(clean_lines)

def main():
    root_dir = Path(__file__).resolve().parent.parent
    input_file = root_dir / "job.json"
    batches_dir = root_dir / "batches"
    batches_dir.mkdir(parents=True, exist_ok=True)

    with open(input_file, "r", encoding="utf-8") as f:
        jobs = json.load(f)

    print(f"Loaded {len(jobs)} jobs from {input_file.name}")

    cleaned_jobs = []
    for idx, job in enumerate(jobs):
        company_info = job.get("company", {}) or {}
        comp_name = company_info.get("name", "")
        
        cleaned_job = {
            "index": idx + 1,
            "id": job.get("id"),
            "title": job.get("title", "").strip(),
            "company_name": comp_name.strip(),
            "salary": job.get("salary", "").strip(),
            "locations": job.get("short_cities", "").strip(),
            "experience": job.get("experience", "").strip(),
            "deadline": job.get("deadline", "").strip(),
            "url": job.get("url", "").strip(),
            "job_description": clean_html(job.get("job_description", "")),
            "job_requirement": clean_html(job.get("job_requirement", "")),
            "job_benefit": clean_html(job.get("job_benefit", ""))
        }
        cleaned_jobs.append(cleaned_job)

    # Batching: ~35 jobs per batch
    batch_size = 35
    total_batches = (len(cleaned_jobs) + batch_size - 1) // batch_size

    for b in range(total_batches):
        batch_slice = cleaned_jobs[b * batch_size : (b + 1) * batch_size]
        batch_filename = batches_dir / f"batch_{b+1:02d}.json"
        with open(batch_filename, "w", encoding="utf-8") as f:
            json.dump(batch_slice, f, ensure_ascii=False, indent=2)
        print(f"Saved Batch {b+1:02d} ({len(batch_slice)} jobs) -> {batch_filename.name}")

    # Summary
    print(f"\nSuccessfully split {len(cleaned_jobs)} jobs into {total_batches} batches in '{batches_dir.name}/'.")

if __name__ == "__main__":
    main()
