import json
import os
import re

# Các từ khóa loại trừ hoàn toàn (Hard Disqualifiers)
HARD_EXCLUDE_KEYWORDS = [
    # Kỹ thuật phần mềm / IT sâu
    'java developer', 'backend developer', 'frontend developer', 'fullstack developer', 
    'mobile developer', 'react js', '.net', 'c#', 'php developer', 'database engineer', 
    'dba', 'devops', 'manual tester', 'automation tester', 'embedded', 'vi điều khiển',
    'kỹ sư phần mềm', 'lập trình viên',
    
    # Kế toán chuyên sâu / Kế toán trưởng
    'kế toán trưởng', 'chief accountant', 'kế toán thuế', 'kế toán tổng hợp', 'kế toán sản xuất', 
    'kế toán xây dựng', 'senior accountant', 'kiểm toán viên',
    
    # Quản lý cấp cao / Lãnh đạo
    'giám đốc', 'phó giám đốc', 'trưởng phòng', 'head of', 'quản đốc', 'trưởng xưởng',
    'banquet sales manager',
    
    # Kỹ thuật công trình / Cơ điện / Xây dựng hiện trường
    'kỹ sư xây dựng', 'giám sát thi công', 'kỹ sư hiện trường', 'kỹ sư mep', 'kỹ sư kết cấu',
    'kỹ sư pccc', 'kỹ sư trắc địa', 'land surveyor', 'kỹ thuật trắc địa', 'kỹ sư hạ tầng',
    'kỹ sư giao thông', 'kỹ sư cơ khí', 'kỹ sư điện', 'kỹ sư bảo trì', 'kỹ thuật viên bảo trì',
    'thợ hàn', 'thợ điện', 'vận hành máy', 'lò hơi', 'nồi hơi', 'cán bộ hồ sơ - nội nghiệp',
    
    # Y tế chuyên môn / Giáo dục đặc thù
    'bác sĩ', 'điều dưỡng', 'y sĩ', 'dược sĩ', 'vật lý trị liệu', 'y học cổ truyền',
    'giáo viên vật lý', 'giáo viên mầm non', 'giáo viên tiếng nhật', 'giảng viên đại học',
    'huấn luyện viên cờ vua',
    
    # Bảo hiểm nhân thọ (mô hình đại lý hoa hồng / tuyển dụng)
    'bảo hiểm nhân thọ', 'prudential', 'manulife', 'dai-ichi', 'sun life', 'bảo việt nhân thọ',
    'fwd', 'chubb life', 'đức minh hưng thịnh'
]

# Chức danh quản lý loại trừ nếu là Level cao
EXCLUDE_TITLES = [
    'trưởng phòng', 'giám đốc', 'phó giám đốc', 'quản đốc', 'trưởng ban', 'chief'
]

def is_hard_excluded(job):
    title = job.get('title', '').lower()
    company = job.get('company_name', '').lower()
    desc = job.get('job_description', '').lower()
    exp = job.get('experience', '').lower()
    req = job.get('job_requirement', '').lower()
    
    # Kiểm tra kinh nghiệm > 3 năm
    if any(e in exp for e in ['trên 5 năm', '5 năm', '4 năm', '3 năm']):
        return True, "Yêu cầu kinh nghiệm từ 3-5+ năm trở lên"
        
    for kw in HARD_EXCLUDE_KEYWORDS:
        if kw in title or kw in company:
            return True, f"Ngành nghề kỹ thuật/chuyên môn sâu hoặc bảo hiểm ({kw})"
            
    # Kiểm tra chức danh quản lý cao cấp
    for t in EXCLUDE_TITLES:
        if t in title and 'trợ lý' not in title:
            return True, f"Vị trí cấp quản lý/lãnh đạo ({t})"
            
    # Kiểm tra telesales gọi lạnh số lượng lớn (sweatshop)
    if 'telesale' in title and ('6 triệu' in desc or '5 triệu' in desc or '4 triệu' in desc):
        if '100' in desc or 'cuộc gọi' in desc or 'gọi điện thoại liên tục' in desc:
            return True, "Telesales gọi lạnh áp lực cao, lương cứng thấp"
            
    # Kiểm tra nếu là thiết kế kỹ thuật công trình
    if 'thiết kế kết cấu' in title or 'thiết kế cơ điện' in title or 'shopdrawing' in title:
        return True, "Thiết kế kỹ thuật công trình/AutoCAD cơ khí kết cấu"

    return False, ""

def classify_job(job):
    title = job.get('title', '').lower()
    desc = job.get('job_description', '').lower()
    req = job.get('job_requirement', '').lower()
    sal = job.get('salary', '')
    exp = job.get('experience', '')
    comp = job.get('company_name', '')
    
    # Phân loại vai trò
    category = "Khác"
    if any(k in title for k in ['admin', 'trợ lý', 'điều phối', 'kế hoạch', 'hỗ trợ', 'văn phòng', 'chứng từ']):
        category = "Vận hành / Điều phối / Back-office / Admin"
    elif any(k in title for k in ['tour', 'du lịch', 'inbound', 'outbound', 'ticketing', 'vé máy bay']):
        category = "Du lịch / Tour Inbound-Outbound / Vé máy bay"
    elif any(k in title for k in ['bất động sản', 'bđs', 'căn hộ', 'mặt bằng', 'nhà đất', 'leasing', 'cho thuê']):
        category = "Bất động sản / Quản lý tài sản / Cho thuê"
    elif any(k in title for k in ['cskh', 'chăm sóc khách hàng', 'customer success', 'customer care', 'hỗ trợ khách hàng']):
        category = "Chăm sóc khách hàng / Customer Success B2B"
    elif any(k in title for k in ['content', 'marketing', 'social', 'truyền thông', 'copywriter', 'seo', 'media']):
        category = "Marketing / Content / Truyền thông"
    elif any(k in title for k in ['nhân sự', 'tuyển dụng', 'hr', 'talent acquisition']):
        category = "Nhân sự / Hành chính nhân sự"
    elif any(k in title for k in ['xuất nhập khẩu', 'logistics', 'mua hàng', 'purchasing', 'thu mua']):
        category = "Logistics / Xuất nhập khẩu / Thu mua"
    elif any(k in title for k in ['b2b', 'account executive', 'kinh doanh', 'sales', 'tư vấn', 'phát triển thị trường']):
        category = "Kinh doanh B2B / Account Executive / Tư vấn"

    # Đánh giá Tier
    # Tier 1: Rất hợp (Fresh/Junior, Lương cứng tốt, Back-office/Admin/B2B Inbound/Tour Inbound/BĐS không ép sales độc hại)
    # Tier 2: Tiềm năng mở rộng (Sales B2B, Marketing, Retail Supervisor, XNK, HR - có thể apply nếu muốn đa dạng cơ hội)
    tier = 2
    reason = []
    
    # Điểm cộng
    if any(k in title for k in ['admin', 'kế hoạch', 'điều phối', 'chứng từ', 'back-office']):
        tier = 1
        reason.append("Công việc back-office / điều phối nội bộ, không chịu áp lực tìm khách")
    if any(k in title for k in ['tour inbound', 'tiếng anh', 'english', 'quốc tế']) or 'toeic' in req or 'tiếng anh' in req:
        tier = 1
        reason.append("Tận dụng lợi thế tiếng Anh / TOEIC 855")
    if any(k in title for k in ['căn hộ', 'bđs', 'bất động sản']) and 'môi giới' not in title:
        tier = 1
        reason.append("Khớp nối chuyên ngành BĐS NEU và 1 năm thực tập")
    if 'không yêu cầu kinh nghiệm' in exp.lower() or 'dưới 1 năm' in exp.lower() or 'chưa có kinh nghiệm sẽ được đào tạo' in req.lower():
        reason.append("Thân thiện với ứng viên ít kinh nghiệm, có đào tạo")
    if 'data có sẵn' in title or 'data sẵn' in title or 'không gọi lạnh' in desc or '100% data' in desc:
        tier = 1
        reason.append("Công ty cấp sẵn data khách hàng, không phải gọi lạnh tìm khách")
        
    return tier, category, " | ".join(reason) if reason else "Vị trí Junior/Fresher có tiềm năng phát triển"

def main():
    all_shortlist = []
    batch_summaries = {}
    
    for b in range(1, 21):
        fname = f"batches/batch_{b:02d}.json"
        if not os.path.exists(fname): continue
        with open(fname, 'r', encoding='utf-8') as f:
            jobs = json.load(f)
            
        tier1_jobs = []
        tier2_jobs = []
        excluded_jobs = []
        
        for j in jobs:
            is_exc, exc_reason = is_hard_excluded(j)
            if is_exc:
                excluded_jobs.append((j, exc_reason))
            else:
                tier, cat, reason = classify_job(j)
                j_info = {
                    'batch': b,
                    'index': j['index'],
                    'id': j['id'],
                    'title': j['title'],
                    'company_name': j['company_name'],
                    'salary': j['salary'],
                    'experience': j['experience'],
                    'locations': j['locations'],
                    'url': j['url'],
                    'category': cat,
                    'tier': tier,
                    'reason': reason,
                    'job_description': j.get('job_description', '')[:300] + '...',
                    'job_benefit': j.get('job_benefit', '')[:250] + '...'
                }
                if tier == 1:
                    tier1_jobs.append(j_info)
                else:
                    tier2_jobs.append(j_info)
                    
                all_shortlist.append(j_info)
                
        batch_summaries[b] = {
            'total': len(jobs),
            'tier1': tier1_jobs,
            'tier2': tier2_jobs,
            'excluded_count': len(excluded_jobs)
        }
        
        # Ghi file review cho từng batch
        review_fname = f"reviews/review_batch_{b:02d}.md"
        with open(review_fname, 'w', encoding='utf-8') as rf:
            rf.write(f"# Đánh Giá Chi Tiết Tuyển Dụng - Batch {b:02d}\n\n")
            rf.write(f"- **Tổng số tin trong file:** {len(jobs)}\n")
            rf.write(f"- **🌟 Tier 1 (Khuyên nộp / Rất phù hợp):** {len(tier1_jobs)}\n")
            rf.write(f"- **🎯 Tier 2 (Tiềm năng mở rộng / Đáng cân nhắc):** {len(tier2_jobs)}\n")
            rf.write(f"- **⛔ Loại bỏ (Kỹ thuật/Senior/Bảo hiểm/Quản lý):** {len(excluded_jobs)}\n\n")
            rf.write("---\n\n")
            
            if tier1_jobs:
                rf.write("## 🌟 VIỆC LÀM TIER 1 (ƯU TIÊN HÀNG ĐẦU)\n\n")
                for item in tier1_jobs:
                    rf.write(f"### Job #{item['index']}: [{item['title']}]({item['url']})\n")
                    rf.write(f"- **Công ty:** {item['company_name']}\n")
                    rf.write(f"- **Mức lương:** `{item['salary']}` | **Kinh nghiệm:** `{item['experience']}` | **Khu vực:** `{item['locations']}`\n")
                    rf.write(f"- **Nhóm vai trò:** {item['category']}\n")
                    rf.write(f"- **Lý do chọn:** {item['reason']}\n\n")
                    
            if tier2_jobs:
                rf.write("## 🎯 VIỆC LÀM TIER 2 (TIỀM NĂNG MỞ RỘNG / CÂN NHẮC THÊM)\n\n")
                for item in tier2_jobs:
                    rf.write(f"### Job #{item['index']}: [{item['title']}]({item['url']})\n")
                    rf.write(f"- **Công ty:** {item['company_name']}\n")
                    rf.write(f"- **Mức lương:** `{item['salary']}` | **Kinh nghiệm:** `{item['experience']}` | **Khu vực:** `{item['locations']}`\n")
                    rf.write(f"- **Nhóm vai trò:** {item['category']}\n")
                    rf.write(f"- **Ghi chú:** {item['reason']}\n\n")

    print(f"Completed analysis of 20 batches!")
    print(f"Total shortlisted jobs (Tier 1 + Tier 2): {len(all_shortlist)}")
    t1_total = sum(len(s['tier1']) for s in batch_summaries.values())
    t2_total = sum(len(s['tier2']) for s in batch_summaries.values())
    print(f"- Tier 1: {t1_total} jobs")
    print(f"- Tier 2: {t2_total} jobs")
    
    # Lưu file JSON trung gian các job đã lọc
    with open('filtered_all_jobs.json', 'w', encoding='utf-8') as out_f:
        json.dump(all_shortlist, out_f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
