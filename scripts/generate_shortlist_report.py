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

    # Sort by score descending
    tier_a.sort(key=lambda x: x["score"], reverse=True)
    tier_b.sort(key=lambda x: x["score"], reverse=True)

    # Group Tier A by role category
    categories = defaultdict(list)
    for j in tier_a:
        categories[j["role_category"]].append(j)

    with open(output_file, "w", encoding="utf-8") as out:
        out.write("# BÁO CÁO VIỆC LÀM PHÙ HỢP NHẤT CHO CẤP ĐỘ FRESHER / JUNIOR (TOPCV SHORTLIST)\n\n")
        out.write("> **Ứng viên:** Cử nhân BĐS (ĐH Kinh tế Quốc dân) | **Ngoại ngữ:** TOEIC 855 | **Kinh nghiệm:** ~1 năm thực tập tại 2 công ty (chưa tự tin kinh nghiệm chuyên môn sâu, cần môi trường đào tạo/hướng dẫn bài bản).\n\n")
        out.write("---\n\n")

        out.write("## I. TỔNG QUAN KẾT QUẢ SÀNG LỌC THỰC TẾ (REALISTIC SCREENING)\n\n")
        out.write("Sau khi bổ sung điều kiện **chỉ chọn các vị trí phù hợp với 1 năm thực tập và loại bỏ triệt để các vị trí đòi hỏi kinh nghiệm chuyên môn sâu hoặc quản lý (Trưởng phòng/Leader/Senior)**, kết quả sàng lọc 672 việc làm TopCV như sau:\n\n")
        out.write("| Phân hạng | Số lượng | Tỷ lệ | Định nghĩa & Mức độ tự tin ứng tuyển |\n")
        out.write("| :--- | :---: | :---: | :--- |\n")
        out.write(f"| 🌟 **Tier A (Khuyên nộp ngay)** | **{len(tier_a)}** | **{len(tier_a)/len(jobs)*100:.1f}%** | Vị trí Junior / Fresher / Coordinator / Assistant, chấp nhận đào tạo từ đầu, không đòi hỏi kinh nghiệm sâu, lương cứng từ 8 - 15M, tận dụng tiếng Anh TOEIC 855 và bằng BĐS NEU. |\n")
        out.write(f"| 🎯 **Tier B (Cân nhắc thêm)** | **{len(tier_b)}** | **{len(tier_b)/len(jobs)*100:.1f}%** | Vị trí Marketing/Content/Sales B2B mở rộng, có thể thử sức nếu muốn đa dạng cơ hội. |\n")
        out.write(f"| ⛔ **Tier C (Đã loại bỏ)** | **{len(jobs) - len(tier_a) - len(tier_b)}** | **{(len(jobs) - len(tier_a) - len(tier_b))/len(jobs)*100:.1f}%** | Đã loại: Trưởng phòng, Quản lý, Lead, Senior (cần >= 2-3 năm exp), Kỹ thuật/Dev/Kế toán, Telesales data rác, 100% hoa hồng. |\n\n")

        out.write("---\n\n")

        out.write("## II. BẢNG XẾP HẠNG TOP VIỆC LÀM TIER A DÀNH CHO JUNIOR THEO TỪNG NHÓM NGHỀ\n\n")

        cat_order = [
            "Sales Coordinator / Admin Junior",
            "Project Assistant / Coordinator",
            "Customer Success Junior",
            "Research & Market Analysis",
            "B2B Account Junior",
            "Marketing / Content Junior",
            "Tư vấn & Kinh doanh tổng quát"
        ]

        for cat in cat_order:
            cat_jobs = categories.get(cat, [])
            if not cat_jobs:
                continue

            out.write(f"### 🎯 Nhóm: {cat.upper()} ({len(cat_jobs)} vị trí phù hợp)\n\n")
            out.write("| Stt | Vị trí công việc | Doanh nghiệp | Mức lương | Kinh nghiệm | Link ứng tuyển |\n")
            out.write("| :-: | :--- | :--- | :--- | :-: | :--- |\n")
            for i, j in enumerate(cat_jobs, 1):
                title_clean = j['title'].replace('|', '-')
                comp_clean = j['company_name'].replace('|', '-')
                out.write(f"| {i} | **{title_clean}** | {comp_clean} | `{j['salary']}` | `{j['experience']}` | [Xem JD & Nộp]({j['url']}) |\n")
            out.write("\n")

            out.write("#### 🔍 Phân tích chi tiết các Job tiêu biểu trong nhóm này:\n\n")
            for j in cat_jobs[:4]:  # Top 4 each
                out.write(f"##### 📌 #{j['index']} [{j['title']}]({j['url']})\n")
                out.write(f"- **Công ty:** {j['company_name']} | **Địa điểm:** {j['locations']} | **Yêu cầu KN:** {j['experience']}\n")
                out.write(f"- **Mức lương:** `{j['salary']}` | **Điểm phù hợp:** `{j['score']}/100`\n")
                out.write("- **Tại sao bạn hoàn toàn tự tin ứng tuyển:**\n")
                for p in j['pros']:
                    out.write(f"  + {p}\n")
                if j['cons']:
                    out.write("- **Điểm lưu ý:**\n")
                    for c in j['cons']:
                        out.write(f"  - {c}\n")
                out.write(f"- **Chiến lược viết CV:** *{j['cv_highlight']}*\n\n")

            out.write("---\n\n")

        out.write("## III. CHIẾN LƯỢC ỨNG TUYỂN DÀNH CHO ỨNG VIÊN 1 NĂM THỰC TẬP (TỰ TIN VƯỢT QUA VÒNG CV)\n\n")
        out.write("Khi chưa có nhiều kinh nghiệm chuyên môn sâu, **bí quyết chiến thắng** của bạn nằm ở 4 điểm mấu chốt:\n\n")
        out.write("1. **Định vị bản thân là 'Nền tảng tốt, học nhanh, cẩn thận':** Nhấn mạnh xuất thân từ **Đại học Kinh tế Quốc dân (NEU)** và điểm số **TOEIC 855**. Nhà tuyển dụng ở cấp độ Junior cực kỳ thích ứng viên có tư duy tốt, tiếng Anh tốt và thái độ chủ động.\n")
        out.write("2. **Quy đổi kinh nghiệm thực tập thành 'Kỹ năng thực chiến':**\n")
        out.write("   - Thay vì nói *'Tôi chỉ mới thực tập'*, hãy viết: *'Đã có 1 năm trải nghiệm thực tế tại 2 doanh nghiệp trong việc tìm hiểu quy hoạch dự án, nghiên cứu thị trường, soạn thảo nội dung truyền thông và hỗ trợ chăm sóc khách hàng 1-1.'*\n")
        out.write("3. **Nhắm vào công việc 'Điều phối & Quy trình' thay vì 'Bán hàng gánh số':** Các vị trí **Sales Coordinator, Sales Admin, Project Assistant** tuyển người cẩn thận, biết làm hợp đồng báo giá, phối hợp team. Bạn hoàn toàn làm tốt công việc này ngay trong tháng đầu tiên.\n")
        out.write("4. **Tận dụng đòn bẩy Tiếng Anh (TOEIC 855):** Rất nhiều ứng viên BĐS hoặc Sales yếu tiếng Anh. Khi bạn nộp vào các công ty dịch vụ quốc tế, xuất nhập khẩu, hoặc doanh nghiệp B2B, điểm TOEIC 855 giúp bạn vượt qua 90% ứng viên cùng lứa tuổi.\n\n")

        out.write("---\n\n")

        out.write("## IV. 5 CÂU HỎI THÔNG MINH ĐỂ HỎI NHÀ TUYỂN DỤNG KHI PHỎNG VẤN\n\n")
        out.write("Để tránh rơi vào tình trạng 'bị thả nổi tự bơi' hoặc áp lực không đúng định hướng:\n\n")
        out.write("1. *'Dạ cho em hỏi trong tháng đầu tiên nhận việc, quy trình đào tạo (onboarding) và làm quen sản phẩm/quy trình của công ty sẽ được diễn ra như thế nào ạ?'*\n")
        out.write("2. *'Ở vị trí này, em sẽ làm việc trực tiếp dưới sự hướng dẫn của ai (Trưởng nhóm hay Quản lý bộ phận) ạ?'*\n")
        out.write("3. *'Công ty đánh giá một nhân sự mới hoàn thành tốt thời gian thử việc dựa trên những tiêu chí hoặc cột mốc cụ thể nào ạ?'*\n")
        out.write("4. *'Trong cơ cấu công việc hàng ngày, thời gian cho việc xử lý giấy tờ/điều phối nội bộ và thời gian giao tiếp với khách hàng bên ngoài phân bổ khoảng bao nhiêu % ạ?'*\n")
        out.write("5. *'Mức lương cứng cố định hàng tháng đã bao gồm những khoản phụ cấp nào và chế độ xem xét tăng lương sau 6 tháng/1 năm của công ty như thế nào ạ?'*\n")

    print("Successfully updated final_job_shortlist.md")

if __name__ == "__main__":
    main()
