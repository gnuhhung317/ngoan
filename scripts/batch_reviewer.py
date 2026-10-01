import json
import re
from pathlib import Path

def score_job(job):
    """
    Evaluates a single job dictionary based on the candidate profile & rubric in candidate_profile.md.
    Returns:
      score: float (0 - 100)
      tier: 'Tier A' | 'Tier B' | 'Tier C'
      role_category: str
      pros: list of str
      cons: list of str
      cv_highlight: str
      flags: list of str
    """
    title = job.get("title", "").lower()
    desc = job.get("job_description", "").lower()
    req = job.get("job_requirement", "").lower()
    benefit = job.get("job_benefit", "").lower()
    salary = job.get("salary", "").lower()
    full_text = f"{title}\n{desc}\n{req}\n{benefit}"

    pros = []
    cons = []
    flags = []
    
    # -------------------------------------------------------------
    # 1. HARD DISQUALIFIERS / RED FLAGS (Tier C immediately)
    # -------------------------------------------------------------
    # Dev / Tech engineering
    if re.search(r'\b(lập trình|developer|frontend|backend|fullstack|devops|tester|qa/qc|it helpdesk|kỹ sư cơ điện|kỹ sư xây dựng|kỹ sư cầu đường|chỉ huy trưởng|giám sát thi công|bác sĩ|dược sĩ|y tá|lái xe|bảo vệ|đầu bếp|phục vụ|thu ngân|công nhân)\b', title):
        return 0, 'Tier C', 'Không liên quan (Kỹ thuật/Y tế/Lao động phổ thông)', [], ['Vị trí chuyên môn kỹ thuật hoặc lao động khác ngành'], '', ['Lệch ngành hoàn toàn']

    # Heavy Finance / Accounting
    if re.search(r'\b(kế toán tổng hợp|kế toán trưởng|kiểm toán|thủ quỹ)\b', title):
        return 0, 'Tier C', 'Kế toán / Kiểm toán', [], ['Vị trí kế toán chuyên môn sâu'], '', ['Lệch chuyên môn']

    # Pure Telesales / Cold call spam
    if re.search(r'\b(telesale|telesales|tele sale|tele marketing|gọi data|cuộc gọi/ngày|telesale tài chính|telesale chứng khoán)\b', title) or \
       re.search(r'\b(100-200 cuộc|150 cuộc|gọi điện theo danh sách data có sẵn)\b', desc + req):
        flags.append("Telesales gọi data liên tục")
        cons.append("Yêu cầu gọi điện thoại số lượng lớn mỗi ngày - Trái định hướng")

    # 100% Commission / No base salary
    if re.search(r'\b(không lương cứng|chỉ hưởng hoa hồng|thu nhập không giới hạn|hưởng 100% hoa hồng)\b', full_text) or \
       (re.search(r'\b(hoa hồng cao|hoa hồng lên đến)\b', full_text) and not re.search(r'\b(lương cứng|lương cơ bản|lương net|lương gross)\b', full_text) and 'triệu' not in salary and 'thỏa thuận' not in salary):
        flags.append("Thu nhập dựa vào hoa hồng, không rõ lương cứng")
        cons.append("Lương không ổn định hoặc phụ thuộc hoàn toàn vào doanh số")

    # -------------------------------------------------------------
    # 2. ROLE CATEGORY & BASE MATCHING (Max 40 pts)
    # -------------------------------------------------------------
    role_score = 0
    role_cat = "Khác"

    # Category 1: Sales Coordinator / Support / Admin / Operations
    if re.search(r'\b(sales coordinator|sales support|sales admin|hỗ trợ kinh doanh|điều phối kinh doanh|sales operations|trợ lý kinh doanh|business assistant)\b', title):
        role_cat = "Sales Coordinator / Support"
        role_score = 38
        pros.append("Đúng nhóm ưu tiên số 1: Điều phối, hỗ trợ vận hành kinh doanh, làm hợp đồng & báo giá")
    elif re.search(r'\b(điều phối|coordinator|hỗ trợ|support|admin)\b', title) and re.search(r'\b(kinh doanh|bán hàng|khách hàng|dự án)\b', title):
        role_cat = "Sales Coordinator / Support"
        role_score = 36
        pros.append("Vị trí điều phối/hỗ trợ gắn liền với hoạt động kinh doanh")

    # Category 2: Project Coordinator / Project Assistant / Real Estate Development / Research
    elif re.search(r'\b(project coordinator|project assistant|trợ lý dự án|điều phối dự án|quản lý dự án|phát triển dự án|project executive)\b', title):
        role_cat = "Project Coordinator / Development"
        role_score = 38
        pros.append("Đúng nhóm ưu tiên: Điều phối dự án, theo dõi tiến độ, phù hợp nền tảng BĐS NEU")
    elif re.search(r'\b(nghiên cứu thị trường|market research|research executive|research analyst|phân tích thị trường)\b', title):
        role_cat = "Research & Market Analysis"
        role_score = 36
        pros.append("Phù hợp năng lực nghiên cứu, phân tích dự án & thị trường")

    # Category 3: B2B Account Executive / Solution Sales / Business Development
    elif re.search(r'\b(account executive|b2b|business development|chuyên viên phát triển kinh doanh|tư vấn giải pháp|partnership|solution consultant|client executive|account management)\b', title):
        role_cat = "B2B Account / Business Development"
        role_score = 36
        pros.append("Kinh doanh giải pháp B2B / Quản lý tài khoản khách hàng, ít áp lực gọi data lạnh")

    # Category 4: Customer Success / Client Experience
    elif re.search(r'\b(customer success|client success|chăm sóc khách hàng b2b|quản lý trải nghiệm khách hàng|cx executive)\b', title):
        role_cat = "Customer Success"
        role_score = 35
        pros.append("Vị trí chăm sóc và phát triển khách hàng sau bán (CS), tập trung giải quyết vấn đề")

    # Category 5: Marketing / Content / Social
    elif re.search(r'\b(marketing coordinator|marketing executive|content marketing|social media|chuyên viên nội dung|truyền thông|copywriter)\b', title):
        role_cat = "Marketing / Content"
        role_score = 28
        pros.append("Tận dụng khả năng viết và biên tập nội dung, phân tích đối tượng")

    # Category 6: Real Estate General Sales / Consultant
    elif re.search(r'\b(bất động sản|bđs|nhân viên kinh doanh|chuyên viên tư vấn|sales executive|nhân viên tư vấn)\b', title):
        role_cat = "Tư vấn & Kinh doanh tổng quát"
        role_score = 18
        pros.append("Vị trí kinh doanh / tư vấn tận dụng được kiến thức ngành")

    else:
        role_score = 10
        role_cat = "Khác"

    # -------------------------------------------------------------
    # 3. LEVERAGE PROFILE: Real Estate, English, Writing (Max 30 pts)
    # -------------------------------------------------------------
    leverage_score = 0
    # Real Estate background match
    if re.search(r'\b(bất động sản|bđs|địa ốc|nhà đất|chủ đầu tư|dự án|tòa nhà|mặt bằng|cho thuê văn phòng|leasing)\b', full_text):
        leverage_score += 12
        pros.append("Thuộc ngành BĐS / Không gian / Văn phòng - Khớp trực tiếp bằng cấp ĐH Kinh tế Quốc dân")
    elif re.search(r'\b(xây dựng|kiến trúc|nội thất|vật liệu|f&b|giáo dục|saas|phần mềm|dịch vụ b2b)\b', full_text):
        leverage_score += 8
        pros.append("Lĩnh vực B2B/Dịch vụ chuyên nghiệp dễ học hỏi và mở rộng")

    # English Requirement / Advantage (TOEIC 855)
    if re.search(r'\b(tiếng anh|english|toeic|ielts|giao tiếp tiếng anh|đọc hiểu tiếng anh|tiếng anh khá|tiếng anh tốt|foreign client|international)\b', full_text):
        leverage_score += 10
        pros.append("Có yêu cầu/ưu tiên tiếng Anh -> Điểm TOEIC 855 tạo lợi thế cạnh tranh vượt trội")

    # Research / Writing / Coordination skills
    if re.search(r'\b(báo cáo|nghiên cứu|soạn thảo|hợp đồng|phối hợp|theo dõi tiến độ|tổng hợp|viết bài|lên kế hoạch)\b', full_text):
        leverage_score += 8
        pros.append("Công việc yêu cầu kỹ năng soạn thảo, điều phối, theo dõi tiến độ")

    # -------------------------------------------------------------
    # 4. SALARY & COMPENSATION (Max 15 pts)
    # -------------------------------------------------------------
    salary_score = 0
    # Analyze salary string
    if any(k in salary for k in ["tới 20", "tới 25", "tới 30", "15 - 20", "12 - 18", "10 - 15", "10 - 20", "12 - 15", "10 - 12", "8 - 12", "8 - 15", "8 - 10", "từ 10", "từ 12", "từ 15"]):
        salary_score = 15
        pros.append(f"Mức lương hấp dẫn: {job.get('salary')} (đạt mức kỳ vọng >= 8-10M)")
    elif any(k in salary for k in ["7 - 10", "6 - 10", "7 - 9", "thỏa thuận", "cạnh tranh", "từ 8"]):
        salary_score = 11
        pros.append(f"Mức lương cạnh tranh / thỏa thuận: {job.get('salary')}")
    elif any(k in salary for k in ["5 - 8", "6 - 8", "dưới 8", "từ 5", "từ 6"]):
        salary_score = 6
        cons.append(f"Mức lương hơi thấp so với kỳ vọng: {job.get('salary')}")
    else:
        salary_score = 8

    # -------------------------------------------------------------
    # 5. GROWTH & CULTURE / ONBOARDING (Max 15 pts)
    # -------------------------------------------------------------
    growth_score = 0
    if re.search(r'\b(đào tạo|onboarding|lộ trình thăng tiến|career path|chuyên viên|leader|mentor|hướng dẫn bài bản)\b', full_text):
        growth_score += 10
        pros.append("Có chính sách đào tạo, hướng dẫn và lộ trình phát triển rõ ràng")
    else:
        growth_score += 5

    if re.search(r'\b(bhxh|bảo hiểm|du lịch|thưởng tháng 13|nghỉ t7|nghỉ thứ 7|nghỉ chủ nhật|lương tháng 13)\b', full_text):
        growth_score += 5
        pros.append("Đầy đủ chế độ phúc lợi (BHXH, thưởng lễ tết, thời gian làm việc chuẩn)")

    # -------------------------------------------------------------
    # TOTAL SCORE CALCULATION & TIER CLASSIFICATION
    # -------------------------------------------------------------
    total_score = min(100, role_score + leverage_score + salary_score + growth_score)

    # Penalties for negative flags
    if flags:
        total_score -= 25 * len(flags)

    total_score = max(0, total_score)

    if total_score >= 70 and not flags and role_cat not in ["Khác", "Kế toán / Kiểm toán"]:
        tier = 'Tier A'
    elif total_score >= 50 and not flags and role_cat not in ["Khác", "Kế toán / Kiểm toán"]:
        tier = 'Tier B'
    else:
        tier = 'Tier C'

    # CV Highlights generator
    cv_highlight = ""
    if role_cat in ["Sales Coordinator / Support", "Project Coordinator / Development"]:
        cv_highlight = "Nhấn mạnh: Khả năng điều phối quy trình, soạn thảo văn bản/báo giá, theo dõi tiến độ dự án, nền tảng phân tích BĐS và tiếng Anh TOEIC 855."
    elif role_cat == "B2B Account / Business Development":
        cv_highlight = "Nhấn mạnh: Kỹ năng tư vấn giải pháp, tìm hiểu nhu cầu B2B, kỹ năng giao tiếp 1-1 tinh tế và khả năng nghiên cứu đối thủ/thị trường."
    elif role_cat == "Research & Market Analysis":
        cv_highlight = "Nhấn mạnh: Bằng BĐS NEU, kinh nghiệm nghiên cứu thị trường, lập báo cáo phân tích, đọc tài liệu tiếng Anh chuyên ngành (TOEIC 855)."
    elif role_cat == "Customer Success":
        cv_highlight = "Nhấn mạnh: Khả năng giải quyết vấn đề, chăm sóc khách hàng doanh nghiệp, tư vấn giải pháp và tinh thần trách nhiệm cao."
    elif role_cat == "Marketing / Content":
        cv_highlight = "Nhấn mạnh: Năng khiếu viết nội dung tự nhiên, tư duy nhạy bén về thị trường và khả năng lên kế hoạch truyền thông bài bản."
    else:
        cv_highlight = "Nhấn mạnh: Tinh thần học hỏi nhanh, nền tảng kinh tế NEU và chứng chỉ TOEIC 855."

    return total_score, tier, role_cat, pros, cons, cv_highlight, flags

def main():
    root_dir = Path(__file__).resolve().parent.parent
    batches_dir = root_dir / "batches"
    reviews_dir = root_dir / "reviews"
    reviews_dir.mkdir(parents=True, exist_ok=True)

    batch_files = sorted(batches_dir.glob("batch_*.json"))
    print(f"Found {len(batch_files)} batch files to review.")

    all_results = []

    for b_file in batch_files:
        batch_num = b_file.stem.replace("batch_", "")
        with open(b_file, "r", encoding="utf-8") as f:
            jobs = json.load(f)

        batch_tier_a = []
        batch_tier_b = []
        batch_tier_c_count = 0

        for job in jobs:
            score, tier, role_cat, pros, cons, cv_hl, flags = score_job(job)
            res_item = {
                "id": job["id"],
                "index": job["index"],
                "title": job["title"],
                "company_name": job["company_name"],
                "salary": job["salary"],
                "locations": job["locations"],
                "experience": job["experience"],
                "url": job["url"],
                "score": score,
                "tier": tier,
                "role_category": role_cat,
                "pros": pros,
                "cons": cons,
                "cv_highlight": cv_hl,
                "flags": flags,
                "batch": batch_num
            }
            all_results.append(res_item)

            if tier == 'Tier A':
                batch_tier_a.append(res_item)
            elif tier == 'Tier B':
                batch_tier_b.append(res_item)
            else:
                batch_tier_c_count += 1

        # Write Batch Review Markdown
        review_md = reviews_dir / f"review_batch_{batch_num}.md"
        with open(review_md, "w", encoding="utf-8") as rf:
            rf.write(f"# Đánh Giá Việc Làm - Batch {batch_num}\n\n")
            rf.write(f"- **Tổng số việc làm trong batch:** {len(jobs)}\n")
            rf.write(f"- **🌟 Tier A (Rất phù hợp):** {len(batch_tier_a)}\n")
            rf.write(f"- **🎯 Tier B (Đáng cân nhắc):** {len(batch_tier_b)}\n")
            rf.write(f"- **⛔ Tier C (Loại bỏ / Red-flags / Không khớp):** {batch_tier_c_count}\n\n")
            rf.write("---\n\n")

            if batch_tier_a:
                rf.write("## 🌟 VIỆC LÀM TIER A (ĐỀ XUẤT HÀNG ĐẦU)\n\n")
                for item in batch_tier_a:
                    rf.write(f"### #{item['index']} [{item['title']}]({item['url']})\n")
                    rf.write(f"- **Công ty:** {item['company_name']}\n")
                    rf.write(f"- **Mức lương:** {item['salary']} | **Kinh nghiệm:** {item['experience']} | **Địa điểm:** {item['locations']}\n")
                    rf.write(f"- **Điểm phù hợp:** `{item['score']}/100` | **Nhóm:** `{item['role_category']}`\n")
                    rf.write("- **Ưu điểm nổi bật:**\n")
                    for p in item['pros']:
                        rf.write(f"  + {p}\n")
                    if item['cons']:
                        rf.write("- **Lưu ý / Rủi ro cần hỏi:**\n")
                        for c in item['cons']:
                            rf.write(f"  - {c}\n")
                    rf.write(f"- **Chiến lược CV:** {item['cv_highlight']}\n\n")

            if batch_tier_b:
                rf.write("## 🎯 VIỆC LÀM TIER B (CÂN NHẮC THÊM)\n\n")
                for item in batch_tier_b:
                    rf.write(f"### #{item['index']} [{item['title']}]({item['url']})\n")
                    rf.write(f"- **Công ty:** {item['company_name']}\n")
                    rf.write(f"- **Mức lương:** {item['salary']} | **Điểm:** `{item['score']}/100` | **Nhóm:** `{item['role_category']}`\n")
                    rf.write("- **Ưu điểm:**\n")
                    for p in item['pros']:
                        rf.write(f"  + {p}\n")
                    if item['cons']:
                        rf.write("- **Lưu ý:**\n")
                        for c in item['cons']:
                            rf.write(f"  - {c}\n")
                    rf.write("\n")

        print(f"Batch {batch_num}: {len(batch_tier_a)} Tier A, {len(batch_tier_b)} Tier B, {batch_tier_c_count} Tier C -> {review_md.name}")

    # Save full evaluated results json for Task 4
    evaluated_file = root_dir / "evaluated_jobs.json"
    with open(evaluated_file, "w", encoding="utf-8") as ef:
        json.dump(all_results, ef, ensure_ascii=False, indent=2)

    tier_a_total = sum(1 for r in all_results if r['tier'] == 'Tier A')
    tier_b_total = sum(1 for r in all_results if r['tier'] == 'Tier B')
    tier_c_total = sum(1 for r in all_results if r['tier'] == 'Tier C')

    print(f"\n=======================================================")
    print(f"SUMMARY EVALUATION ACROSS ALL {len(all_results)} JOBS:")
    print(f"[Tier A] Top Matches: {tier_a_total}")
    print(f"[Tier B] Good Matches: {tier_b_total}")
    print(f"[Tier C] Filtered out: {tier_c_total}")
    print(f"=======================================================\n")

if __name__ == "__main__":
    main()
