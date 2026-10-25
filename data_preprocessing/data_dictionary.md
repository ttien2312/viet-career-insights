# Từ điển dữ liệu VietJobs

Tài liệu mô tả các trường dữ liệu trong các bảng đầu ra.

## jobs_clean

| Tên cột | Mô tả |
|---|---|
| `job_title` | Tên vị trí tuyển dụng |
| `location` | Địa điểm tuyển dụng gốc |
| `country` | Quốc gia tuyển dụng |
| `qualifications` | Yêu cầu trình độ, bằng cấp |
| `technical_skills` | Danh sách kỹ năng chuyên môn gốc |
| `soft_skills` | Danh sách kỹ năng mềm gốc |
| `languages_required` | Yêu cầu ngoại ngữ |
| `experience_required` | Kinh nghiệm yêu cầu dạng văn bản |
| `salary` | Thông tin lương gốc |
| `contract_type` | Loại hợp đồng lao động |
| `working_hours` | Thời gian làm việc |
| `benefits` | Quyền lợi, phúc lợi |
| `description` | Mô tả công việc |
| `requirements_text` | Nội dung yêu cầu tuyển dụng |
| `category` | Mã nhóm nghề gốc |
| `salary_min` | Cận dưới lương trong dữ liệu gốc |
| `salary_max` | Cận trên lương trong dữ liệu gốc |
| `salary_avg` | Thông tin lương trung bình gốc |
| `experience_months` | Kinh nghiệm quy đổi sang tháng |
| `experience_group` | Nhóm mức kinh nghiệm |
| `salary_min_million` | Cận dưới lương sau chuẩn hóa, triệu đồng |
| `salary_max_million` | Cận trên lương sau chuẩn hóa, triệu đồng |
| `salary_status` | Trạng thái thông tin lương |
| `salary_midpoint_million` | Trung điểm khoảng lương, triệu đồng |
| `salary_outlier_flag` | Đánh dấu lương tối đa vượt 100 triệu |
| `salary_usable` | Đánh dấu lương có thể sử dụng theo quy tắc xử lý |
| `salary_for_analysis` | Giá trị lương dùng cho phân tích |
| `location_clean` | Địa điểm sau chuẩn hóa |
| `category_clean` | Tên nhóm nghề đã chuẩn hóa |
| `technical_skills_clean` | Kỹ năng chuyên môn được nối bằng dấu \| |
| `soft_skills_clean` | Kỹ năng mềm được nối bằng dấu \| |
| `job_id` | Mã định danh của tin tuyển dụng |

## skills_table

| Tên cột | Mô tả |
|---|---|
| `job_id` | Mã định danh của tin tuyển dụng |
| `category_clean` | Tên nhóm nghề đã chuẩn hóa |
| `skill` | Một kỹ năng riêng lẻ |
| `skill_type` | Loại kỹ năng: chuyên môn hoặc kỹ năng mềm |
