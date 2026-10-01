import json
from pathlib import Path
from collections import defaultdict

def main():
    root_dir = Path(__file__).resolve().parent.parent
    eval_file = root_dir / "evaluated_jobs.json"
    output_file = root_dir / "final_job_shortlist.md"

    with open(eval_file, "r", encoding="utf-8") as f:
        jobs = json.load(f)

    tier_a = [j for j in jobs if j["tier"] == "Tier A"]
    tier_b = [j for j in jobs if j["tier"] == "Tier B"]

    # Sort Tier A by score descending
    tier_a.sort(key=lambda x: x["score"], reverse=True)
    tier_b.sort(key=lambda x: x["score"], reverse=True)

    # Group Tier A by role category
    categories = defaultdict(list)
    for j in tier_a:
        categories[j["role_category"]].append(j)

    with open(output_file, "w", encoding="utf-8") as out:
        out.write("# BÁO CÁO TỔNG HỢP & BẢNG XẾP HẠNG VIỆC LÀM PHÙ HỢP (TOPCV SHORTLIST)\n\n")
        out.write("> **Dữ liệu phân tích:** 672 việc làm TopCV | **Ứng viên:** Cử nhân BĐS (NEU) - TOEIC 855 - Định hướng Điều phối / B2B Account / Nghiên cứu / Customer Success.\n\n")
        out.write("---\n\n")

        out.write("## I. TỔNG QUAN KẾT QUẢ SÀNG LỌC (EXECUTIVE SUMMARY)\n\n")
        out.write("| Phân hạng | Số lượng | Tỷ lệ | Định nghĩa & Hành động |\n")
        out.write("| :--- | :---: | :---: | :--- |\n")
        out.write(f"| 🌟 **Tier A (Top Matches)** | **{len(tier_a)}** | **{len(tier_a)/len(jobs)*100:.1f}%** | Rất phù hợp (Đúng nhóm ưu tiên: Điều phối / B2B / Dự án / CS, lương tốt, tận dụng BĐS & TOEIC 855) -> **Nộp ngay** |\n")
        out.write(f"| 🎯 **Tier B (Good Potential)** | **{len(tier_b)}** | **{len(tier_b)/len(jobs)*100:.1f}%** | Phù hợp khá tốt (Mở rộng cơ hội Marketing/Content/B2B Sales) -> **Cân nhắc dự phòng** |\n")
        out.write(f"| ⛔ **Tier C (Filtered Out)** | **{len(jobs) - len(tier_a) - len(tier_b)}** | **{(len(jobs) - len(tier_a) - len(tier_b))/len(jobs)*100:.1f}%** | Bị loại do: Lệch ngành (IT, Kế toán, Xây dựng), Telesales gọi data lạnh, 100% hoa hồng không lương cứng |\n\n")

        out.write("---\n\n")

        out.write("## II. BẢNG XẾP HẠNG TOP JOB TIER A THEO TỪNG NHÓM NGHỀ NGHIỆP MỤC TIÊU\n\n")

        # Category Order Priority
        cat_order = [
            "Sales Coordinator / Support",
            "Project Coordinator / Development",
            "B2B Account / Business Development",
            "Customer Success",
            "Research & Market Analysis",
            "Marketing / Content",
            "Tư vấn & Kinh doanh tổng quát"
        ]

        for cat in cat_order:
            cat_jobs = categories.get(cat, [])
            if not cat_jobs:
                continue

            out.write(f"### 🎯 Nhóm: {cat.upper()} ({len(cat_jobs)} vị trí xuất sắc)\n\n")
            out.write("| Stt | Vị trí công việc | Công ty | Mức lương | Điểm | Link TopCV |\n")
            out.write("| :-: | :--- | :--- | :--- | :-: | :--- |\n")
            for i, j in enumerate(cat_jobs, 1):
                title_clean = j['title'].replace('|', '-')
                comp_clean = j['company_name'].replace('|', '-')
                out.write(f"| {i} | **{title_clean}** | {comp_clean} | `{j['salary']}` | `{j['score']}/100` | [Xem JD & Nộp]({j['url']}) |\n")
            out.write("\n")

            out.write("#### 🔍 Phân tích chi tiết các Job tiêu biểu trong nhóm này:\n\n")
            for j in cat_jobs[:5]:  # Top 5 in each category
                out.write(f"##### 📌 #{j['index']} [{j['title']}]({j['url']})\n")
                out.write(f"- **Công ty:** {j['company_name']} | **Địa điểm:** {j['locations']} | **Kinh nghiệm:** {j['experience']}\n")
                out.write(f"- **Mức lương:** `{j['salary']}` | **Điểm phù hợp:** `{j['score']}/100`\n")
                out.write("- **Tại sao khớp hồ sơ:**\n")
                for p in j['pros']:
                    out.write(f"  + {p}\n")
                if j['cons']:
                    out.write("- **Lưu ý / Rủi ro cần hỏi kỹ khi phỏng vấn:**\n")
                    for c in j['cons']:
                        out.write(f"  - {c}\n")
                out.write(f"- **Chiến lược điều chỉnh CV:** *{j['cv_highlight']}*\n\n")

            out.write("---\n\n")

        out.write("## III. CHIẾN LƯỢC ĐIỀU CHỈNH 3 PHIÊN BẢN CV (CV TAILORING MATRIX)\n\n")
        out.write("Để tối đa hóa tỷ lệ nhận lời mời phỏng vấn, bạn nên chuẩn bị 3 bản CV được tinh chỉnh trọng tâm:\n\n")
        
        out.write("### 📄 Phiên bản 1: CV Thiên về Điều phối / Vận hành (Sales & Project Coordinator)\n")
        out.write("- **Dành cho:** Các vị trí *Sales Coordinator, Project Assistant, Operations Support*.\n")
        out.write("- **Tiêu đề CV:** `NGUYỄN VĂN A - SALES / PROJECT COORDINATOR`\n")
        out.write("- **Summary (Giới thiệu):** Cử nhân Bất động sản NEU, TOEIC 855 với tư duy tổ chức logic, thành thạo điều phối quy trình, soạn thảo báo giá/hợp đồng và theo dõi tiến độ công việc giữa các phòng ban.\n")
        out.write("- **Key Skills:** Quản trị quy trình, soạn thảo văn bản thương mại, phối hợp đa phòng ban, phân tích dữ liệu cơ bản, tiếng Anh thương mại.\n\n")

        out.write("### 📄 Phiên bản 2: CV Thiên về Tư vấn Doanh nghiệp (B2B Account / Business Development)\n")
        out.write("- **Dành cho:** Các vị trí *B2B Account Executive, Corporate Sales, Customer Success*.\n")
        out.write("- **Tiêu đề CV:** `NGUYỄN VĂN A - B2B ACCOUNT EXECUTIVE / BUSINESS DEVELOPMENT`\n")
        out.write("- **Summary (Giới thiệu):** Nhân sự kinh doanh định hướng giải pháp, có kinh nghiệm tiếp cận và thấu hiểu nhu cầu khách hàng B2B, tư duy logic, kỹ năng đàm phán 1-1 và tiếng Anh giao dịch lưu loát (TOEIC 855).\n")
        out.write("- **Key Skills:** Consultative Selling, Quản lý quan hệ khách hàng (CRM), đàm phán hợp đồng, phân tích đối thủ cạnh tranh.\n\n")

        out.write("### 📄 Phiên bản 3: CV Thiên về Nghiên cứu & Phát triển Dự án (Market Research / Real Estate Analyst)\n")
        out.write("- **Dành cho:** Các vị trí *Market Research Executive, Real Estate Development Assistant*.\n")
        out.write("- **Tiêu đề CV:** `NGUYỄN VĂN A - REAL ESTATE RESEARCH & DEVELOPMENT SPECIALIST`\n")
        out.write("- **Summary (Giới thiệu):** Tốt nghiệp ngành Bất động sản - ĐH Kinh tế Quốc dân, TOEIC 855. Thế mạnh nghiên cứu thị trường, phân tích dự án, đọc hiểu tài liệu quốc tế và tổng hợp báo cáo chuyên sâu.\n")
        out.write("- **Key Skills:** Nghiên cứu thị trường BĐS, phân tích khả thi dự án, tổng hợp báo cáo thị trường, dịch thuật tài liệu chuyên ngành.\n\n")

        out.write("---\n\n")

        out.write("## IV. BỘ CÂU HỎI CHECK-LIST KHI PHỎNG VẤN ĐỂ LOẠI BỎ RED-FLAGS\n\n")
        out.write("Khi được gọi phỏng vấn, hãy chủ động hỏi các câu sau ở phần Q&A để đảm bảo môi trường làm việc đúng như kỳ vọng:\n\n")
        out.write("1. **Về cơ cấu công việc thực tế:** *'Trong 8 tiếng làm việc hàng ngày, tỷ lệ thời gian giữa việc điều phối/xử lý hồ sơ nội bộ so với việc trực tiếp gọi điện/tiếp xúc khách hàng là bao nhiêu %?'*\n")
        out.write("2. **Về cơ cấu KPI & Thu nhập:** *'Mức lương cứng cố định hàng tháng là bao nhiêu? Tiêu chí đánh giá KPI chính gồm những chỉ số định tính hay doanh số cụ thể nào?'*\n")
        out.write("3. **Về nguồn khách hàng (nếu là B2B/Account):** *'Nguồn khách hàng/đối tác do công ty phân bổ từ marketing/inbound hay nhân sự tự tìm kiếm từ data ngoài?'*\n")
        out.write("4. **Về quy trình đào tạo & Onboarding:** *'Trong 2 tháng thử việc, công ty có chương trình onboarding hoặc người hướng dẫn trực tiếp (Mentor) cho nhân sự mới không?'*\n")
        out.write("5. **Về lộ trình phát triển (Career Path):** *'Sau 1–2 năm làm việc tốt ở vị trí này, lộ trình phát triển lên vị trí Specialist hoặc Team Lead sẽ diễn ra như thế nào?'*\n")

    print(f"Successfully generated Master Shortlist report: {output_file.name}")

if __name__ == "__main__":
    main()
