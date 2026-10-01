import json
import re
from pathlib import Path

def score_job_junior(job):
    """
    Evaluates a single job dictionary based on the updated candidate profile:
    - Junior / Fresher level (~1 year internship across 2 companies)
    - Low confidence in specialized deep expertise
    - Seeking entry/junior roles with onboarding, training, coordination, B2B account, project assistant, research
    - Strong English (TOEIC 855), NEU Real Estate major, good writing/research.
    """
    title = job.get("title", "").lower()
    desc = job.get("job_description", "").lower()
    req = job.get("job_requirement", "").lower()
    benefit = job.get("job_benefit", "").lower()
    salary = job.get("salary", "").lower()
    exp = job.get("experience", "").lower()
    full_text = f"{title}\n{desc}\n{req}\n{benefit}\n{exp}"

    pros = []
    cons = []
    flags = []

    # -------------------------------------------------------------
    # 1. HARD DISQUALIFIERS & SENIORITY / ROLE MISMATCH (Tier C)
    # -------------------------------------------------------------
    # 1.1 Management / Leadership / Senior positions
    if re.search(r'\b(trưởng phòng|phó phòng|trưởng nhóm|team lead|lead|manager|giám đốc|director|chủ trì|chỉ huy trưởng|senior|chuyên gia)\b', title):
        return 0, 'Tier C', 'Vị trí Quản lý / Senior', [], ['Vị trí yêu cầu kinh nghiệm quản lý hoặc cấp bậc Senior - Không phù hợp với cấp độ 1 năm thực tập'], '', ['Quản lý / Senior']

    # 1.2 Non-relevant industries (Tech dev, Construction site eng, Pure medical, Factory labor)
    if re.search(r'\b(lập trình|developer|frontend|backend|fullstack|devops|tester|qa/qc|it helpdesk|kỹ sư cơ điện|kỹ sư xây dựng|kỹ sư kết cấu|bác sĩ|dược sĩ|y tá|lái xe|bảo vệ|đầu bếp|phục vụ|thu ngân|công nhân|thợ hàn|thợ may)\b', title):
        return 0, 'Tier C', 'Lệch ngành kỹ thuật / Lao động', [], ['Lệch ngành chuyên môn kỹ thuật hoặc lao động phổ thông'], '', ['Lệch ngành hoàn toàn']

    # 1.3 Deep Finance / Pure Accounting
    if re.search(r'\b(kế toán tổng hợp|kế toán trưởng|kiểm toán viên|thủ quỹ)\b', title):
        return 0, 'Tier C', 'Kế toán / Kiểm toán', [], ['Vị trí kế toán chuyên môn sâu'], '', ['Lệch chuyên môn']

    # 1.4 Deep Technical Consulting requiring years of experience (e.g. ERP consultant)
    if re.search(r'\b(erp implementation|chuyên viên erp|sap|oracle|triển khai phần mềm chuyên sâu)\b', title + req):
        return 0, 'Tier C', 'Chuyên môn kỹ thuật sâu', [], ['Đòi hỏi kinh nghiệm triển khai kỹ thuật chuyên môn sâu (ERP/SAP)'], '', ['Chuyên môn quá sâu']

    # 1.5 Pure Telesales / Cold Calling Spam
    if re.search(r'\b(telesale|telesales|tele sale|tele marketing|gọi data|cuộc gọi/ngày|telesale tài chính|telesale chứng khoán)\b', title) or \
       re.search(r'\b(100-200 cuộc|150 cuộc|gọi điện theo danh sách data có sẵn|gọi điện liên tục|spam call)\b', desc + req):
        flags.append("Telesales gọi data liên tục")
        cons.append("Yêu cầu gọi điện thoại số lượng lớn mỗi ngày - Trái định hướng")

    # 1.6 100% Commission / No base salary
    if re.search(r'\b(không lương cứng|chỉ hưởng hoa hồng|thu nhập không giới hạn|hưởng 100% hoa hồng)\b', full_text) or \
       (re.search(r'\b(hoa hồng cao|hoa hồng lên đến)\b', full_text) and not re.search(r'\b(lương cứng|lương cơ bản|lương net|lương gross)\b', full_text) and 'triệu' not in salary and 'thỏa thuận' not in salary):
        flags.append("Thu nhập dựa vào hoa hồng, không rõ lương cứng")
        cons.append("Lương không ổn định hoặc phụ thuộc hoàn toàn vào doanh số")

    # 1.7 Strict 2-3+ years of specialized experience
    if re.search(r'\b(từ 2 năm kinh nghiệm|tối thiểu 2 năm|có ít nhất 2 năm|kinh nghiệm từ 2 - 3 năm|3 năm kinh nghiệm|2-3 năm kinh nghiệm)\b', req):
        flags.append("Yêu cầu từ 2 năm kinh nghiệm chuyên môn")
        cons.append("Yêu cầu tối thiểu 2-3 năm kinh nghiệm chuyên sâu - Quá tầm so với cấp độ 1 năm thực tập")

    if exp in ["2 năm", "3 năm", "4 năm", "5 năm"] and not re.search(r'\b(chấp nhận sinh viên|chưa có kinh nghiệm|đào tạo|fresher|intern)\b', full_text):
        flags.append(f"Yêu cầu kinh nghiệm {exp}")
        cons.append(f"Yêu cầu {exp} kinh nghiệm chuyên môn")

    # -------------------------------------------------------------
    # 2. SENIORITY FIT & TRAINING (Max 30 pts)
    # -------------------------------------------------------------
    seniority_score = 0
    if re.search(r'\b(không yêu cầu kinh nghiệm|chưa có kinh nghiệm|chấp nhận sinh viên|mới ra trường|đào tạo từ đầu|được hướng dẫn|fresher|intern|thực tập|trainee|junior)\b', full_text):
        seniority_score = 30
        pros.append("Cực kỳ thân thiện với Fresher/Junior: Chấp nhận chưa có nhiều kinh nghiệm, được đào tạo từ đầu")
    elif exp in ["chưa có kinh nghiệm", "dưới 1 năm", "1 năm"] or re.search(r'\b(kinh nghiệm 1 năm|0 - 1 năm|0-1 năm|dưới 1 năm|ưu tiên có kinh nghiệm là một lợi thế)\b', req + exp):
        seniority_score = 25
        pros.append("Yêu cầu kinh nghiệm 0 - 1 năm: Vừa vặn với 1 năm thực tập tại 2 công ty")
    elif exp == "không yêu cầu":
        seniority_score = 25
        pros.append("Không yêu cầu kinh nghiệm cứng")
    else:
        seniority_score = 10
        cons.append("Cần xem xét kỹ yêu cầu kinh nghiệm thực tế")

    # -------------------------------------------------------------
    # 3. ROLE CATEGORY & SUITABILITY (Max 30 pts)
    # -------------------------------------------------------------
    role_score = 0
    role_cat = "Khác"

    # Category 1: Sales Coordinator / Sales Admin Junior / Support
    if re.search(r'\b(sales coordinator|sales support|sales admin|hỗ trợ kinh doanh|điều phối kinh doanh|sales operations|trợ lý kinh doanh|business assistant)\b', title):
        role_cat = "Sales Coordinator / Admin Junior"
        role_score = 30
        pros.append("Đúng nhóm ưu tiên số 1: Điều phối kinh doanh, hỗ trợ văn bản/hợp đồng, quy trình rõ ràng")
    elif re.search(r'\b(điều phối|coordinator|hỗ trợ|support|admin)\b', title) and re.search(r'\b(kinh doanh|bán hàng|khách hàng|dự án)\b', title):
        role_cat = "Sales Coordinator / Admin Junior"
        role_score = 28
        pros.append("Vị trí điều phối/hỗ trợ gắn với kinh doanh, quy trình chuẩn")

    # Category 2: Project Assistant / Project Coordinator Junior
    elif re.search(r'\b(project coordinator|project assistant|trợ lý dự án|điều phối dự án|project executive)\b', title):
        role_cat = "Project Assistant / Coordinator"
        role_score = 30
        pros.append("Đúng nhóm ưu tiên số 1: Trợ lý dự án, theo dõi tiến độ, phù hợp bằng BĐS NEU")

    # Category 3: Customer Success / Client Support
    elif re.search(r'\b(customer success|client success|chăm sóc khách hàng b2b|quản lý trải nghiệm|client service)\b', title):
        role_cat = "Customer Success Junior"
        role_score = 28
        pros.append("Đúng nhóm ưu tiên: Chăm sóc khách hàng doanh nghiệp sau bán, giải quyết vấn đề")

    # Category 4: Real Estate Research / Market Research Junior
    elif re.search(r'\b(nghiên cứu thị trường|market research|research executive|research assistant|phân tích thị trường)\b', title):
        role_cat = "Research & Market Analysis"
        role_score = 27
        pros.append("Phù hợp năng lực nghiên cứu, phân tích dự án & thị trường BĐS")

    # Category 5: B2B Account Junior / Business Development Trainee
    elif re.search(r'\b(account executive|b2b|business development|chuyên viên phát triển kinh doanh|tư vấn giải pháp|partnership|account management)\b', title):
        role_cat = "B2B Account Junior"
        role_score = 26
        pros.append("Kinh doanh giải pháp B2B / Quản lý tài khoản khách hàng, ít áp lực gọi data lạnh")

    # Category 6: Marketing Coordinator / Content Junior
    elif re.search(r'\b(marketing coordinator|marketing executive|content marketing|social media|chuyên viên nội dung|marketing assistant)\b', title):
        role_cat = "Marketing / Content Junior"
        role_score = 22
        pros.append("Tận dụng khả năng viết và biên tập nội dung, phân tích đối tượng")

    elif re.search(r'\b(nhân viên kinh doanh|chuyên viên tư vấn|sales executive)\b', title):
        role_cat = "Tư vấn & Kinh doanh tổng quát"
        role_score = 15
        pros.append("Vị trí kinh doanh / tư vấn cơ bản")
    else:
        role_cat = "Khác"
        role_score = 8

    # -------------------------------------------------------------
    # 4. PROFILE LEVERAGE: Real Estate, English, Writing (Max 25 pts)
    # -------------------------------------------------------------
    leverage_score = 0
    # English leverage (TOEIC 855)
    if re.search(r'\b(tiếng anh|english|toeic|ielts|giao tiếp tiếng anh|đọc hiểu tiếng anh|tiếng anh khá|tiếng anh tốt|foreign client|international)\b', full_text):
        leverage_score += 10
        pros.append("Yêu cầu/ưu tiên tiếng Anh -> Điểm TOEIC 855 là đòn bẩy vượt trội so với các ứng viên khác")

    # Real Estate Major Leverage
    if re.search(r'\b(bất động sản|bđs|địa ốc|nhà đất|chủ đầu tư|dự án|tòa nhà|mặt bằng|cho thuê văn phòng|leasing)\b', full_text):
        leverage_score += 8
        pros.append("Lĩnh vực BĐS / Không gian / Văn phòng - Tận dụng tối đa bằng cử nhân BĐS NEU")
    elif re.search(r'\b(giáo dục|saas|phần mềm|dịch vụ doanh nghiệp|b2b|xây dựng|f&b)\b', full_text):
        leverage_score += 5
        pros.append("Lĩnh vực B2B dịch vụ chuyên nghiệp, môi trường văn minh")

    # Writing & Documentation & Coordination
    if re.search(r'\b(báo cáo|hợp đồng|soạn thảo|phối hợp|quy trình|hồ sơ|theo dõi tiến độ|viết bài)\b', full_text):
        leverage_score += 7
        pros.append("Công việc đòi hỏi sự cẩn thận, soạn thảo văn bản, theo dõi tiến độ")

    # -------------------------------------------------------------
    # 5. COMPENSATION & TRAINING / CULTURE (Max 15 pts)
    # -------------------------------------------------------------
    comp_score = 0
    # Base Salary appropriate for Fresher/Junior (7 - 15M)
    if any(k in salary for k in ["8 - 12", "8 - 15", "8 - 10", "7 - 10", "10 - 15", "10 - 12", "12 - 15", "từ 8", "từ 10", "thỏa thuận", "cạnh tranh"]):
        comp_score += 8
        pros.append(f"Mức lương phù hợp với Fresher/Junior: {job.get('salary')}")
    elif any(k in salary for k in ["6 - 8", "7 - 9", "5 - 8"]):
        comp_score += 6
        pros.append(f"Mức lương khởi điểm: {job.get('salary')}")
    else:
        comp_score += 5

    # Training & Onboarding
    if re.search(r'\b(đào tạo|onboarding|hướng dẫn bài bản|được đào tạo|mentor|chỉ dẫn|lộ trình thăng tiến)\b', full_text):
        comp_score += 7
        pros.append("Có quy trình đào tạo và người hướng dẫn bài bản, giảm bớt áp lực tự bơi")
    else:
        comp_score += 3

    # -------------------------------------------------------------
    # TOTAL SCORE & TIER CALCULATION
    # -------------------------------------------------------------
    total_score = seniority_score + role_score + leverage_score + comp_score

    # Heavy penalties for flags
    if flags:
        total_score -= 25 * len(flags)

    total_score = max(0, min(100, total_score))

    # Tier Classification for Junior/Fresher
    if total_score >= 70 and not flags and role_cat not in ["Khác", "Kế toán / Kiểm toán"]:
        tier = 'Tier A'
    elif total_score >= 55 and len(flags) <= 1 and role_cat not in ["Khác", "Kế toán / Kiểm toán"]:
        tier = 'Tier B'
    else:
        tier = 'Tier C'

    # CV Highlights customized for Junior
    cv_highlight = ""
    if role_cat == "Sales Coordinator / Admin Junior":
        cv_highlight = "Nhấn mạnh: Tốt nghiệp NEU, TOEIC 855, tính cách cẩn thận, thành thạo tin học văn phòng, khả năng phối hợp đa phòng ban và tinh thần cầu tiến học hỏi."
    elif role_cat == "Project Assistant / Coordinator":
        cv_highlight = "Nhấn mạnh: Bằng cử nhân BĐS NEU, khả năng nghiên cứu & tổng hợp tài liệu dự án, kỹ năng theo dõi tiến độ và tiếng Anh thương mại 855 TOEIC."
    elif role_cat == "Customer Success Junior":
        cv_highlight = "Nhấn mạnh: Khả năng lắng nghe, thấu hiểu nhu cầu khách hàng, tinh thần trách nhiệm và kỹ năng xử lý tình huống khéo léo."
    elif role_cat == "B2B Account Junior":
        cv_highlight = "Nhấn mạnh: Khả năng nghiên cứu sản phẩm/đối tác, tư duy tư vấn giải pháp văn minh, sẵn sàng học hỏi quy trình kinh doanh B2B."
    elif role_cat == "Research & Market Analysis":
        cv_highlight = "Nhấn mạnh: Nền tảng học thuật BĐS NEU, kỹ năng thu thập và phân tích dữ liệu thị trường, khả năng đọc tài liệu tiếng Anh nhanh."
    elif role_cat == "Marketing / Content Junior":
        cv_highlight = "Nhấn mạnh: Tư duy nội dung tự nhiên, khả năng viết bài đa dạng văn phong và tinh thần bắt nhịp xu hướng nhanh."
    else:
        cv_highlight = "Nhấn mạnh: Nền tảng ĐH Kinh tế Quốc dân, TOEIC 855 và thái độ làm việc nghiêm túc, sẵn sàng đào tạo."

    return total_score, tier, role_cat, pros, cons, cv_highlight, flags

def main():
    root_dir = Path(__file__).resolve().parent.parent
    batches_dir = root_dir / "batches"
    reviews_dir = root_dir / "reviews"
    reviews_dir.mkdir(parents=True, exist_ok=True)

    batch_files = sorted(batches_dir.glob("batch_*.json"))
    all_results = []

    for b_file in batch_files:
        batch_num = b_file.stem.replace("batch_", "")
        with open(b_file, "r", encoding="utf-8") as f:
            jobs = json.load(f)

        batch_tier_a = []
        batch_tier_b = []
        batch_tier_c_count = 0

        for job in jobs:
            score, tier, role_cat, pros, cons, cv_hl, flags = score_job_junior(job)
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
            rf.write(f"# Đánh Giá Việc Làm - Batch {batch_num} (Dành cho Fresher/Junior)\n\n")
            rf.write(f"- **Tổng số việc làm trong batch:** {len(jobs)}\n")
            rf.write(f"- **🌟 Tier A (Khuyên nộp ngay - Phù hợp Junior):** {len(batch_tier_a)}\n")
            rf.write(f"- **🎯 Tier B (Đáng cân nhắc):** {len(batch_tier_b)}\n")
            rf.write(f"- **⛔ Tier C (Loại bỏ - Cần kinh nghiệm sâu/Quản lý/Telesales):** {batch_tier_c_count}\n\n")
            rf.write("---\n\n")

            if batch_tier_a:
                rf.write("## 🌟 VIỆC LÀM TIER A (PHÙ HỢP NHẤT VỚI 1 NĂM THỰC TẬP)\n\n")
                for item in batch_tier_a:
                    rf.write(f"### #{item['index']} [{item['title']}]({item['url']})\n")
                    rf.write(f"- **Công ty:** {item['company_name']}\n")
                    rf.write(f"- **Mức lương:** `{item['salary']}` | **Yêu cầu KN:** `{item['experience']}` | **Địa điểm:** {item['locations']}\n")
                    rf.write(f"- **Điểm phù hợp:** `{item['score']}/100` | **Nhóm:** `{item['role_category']}`\n")
                    rf.write("- **Ưu điểm nổi bật:**\n")
                    for p in item['pros']:
                        rf.write(f"  + {p}\n")
                    if item['cons']:
                        rf.write("- **Lưu ý cần hỏi thêm:**\n")
                        for c in item['cons']:
                            rf.write(f"  - {c}\n")
                    rf.write(f"- **Chiến lược CV:** *{item['cv_highlight']}*\n\n")

            if batch_tier_b:
                rf.write("## 🎯 VIỆC LÀM TIER B (CÂN NHẮC THÊM)\n\n")
                for item in batch_tier_b:
                    rf.write(f"### #{item['index']} [{item['title']}]({item['url']})\n")
                    rf.write(f"- **Công ty:** {item['company_name']}\n")
                    rf.write(f"- **Mức lương:** `{item['salary']}` | **Điểm:** `{item['score']}/100` | **Nhóm:** `{item['role_category']}`\n")
                    rf.write("- **Ưu điểm:**\n")
                    for p in item['pros']:
                        rf.write(f"  + {p}\n")
                    if item['cons']:
                        rf.write("- **Lưu ý:**\n")
                        for c in item['cons']:
                            rf.write(f"  - {c}\n")
                    rf.write("\n")

    # Save full evaluated results json
    evaluated_file = root_dir / "evaluated_jobs.json"
    with open(evaluated_file, "w", encoding="utf-8") as ef:
        json.dump(all_results, ef, ensure_ascii=False, indent=2)

    tier_a_total = sum(1 for r in all_results if r['tier'] == 'Tier A')
    tier_b_total = sum(1 for r in all_results if r['tier'] == 'Tier B')
    tier_c_total = sum(1 for r in all_results if r['tier'] == 'Tier C')

    print(f"DONE EVALUATION:")
    print(f"Tier A (Junior Matches): {tier_a_total}")
    print(f"Tier B (Potential): {tier_b_total}")
    print(f"Tier C (Excluded): {tier_c_total}")

if __name__ == "__main__":
    main()
