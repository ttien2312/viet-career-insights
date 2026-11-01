# viet-career-insights
An information visualization project exploring Vietnam's labor market to help high school students make informed career decisions.

Bài tập lớn cuối kỳ môn **Trực quan hóa thông tin** – Nhóm 15.
Đề tài: đóng vai cố vấn hướng nghiệp, giúp học sinh THPT chọn ngành học phù hợp với thị trường lao động Việt Nam (dữ liệu chính: VietJobs).

## Cấu trúc thư mục

```
viet-career-insights/
├── data_preprocessing/        # TV1 – làm sạch dữ liệu
│   ├── notebooks/preprocessing.ipynb
│   └── data/                  # jobs_clean.csv.gz, skills_table.csv, quality_comparison.csv, ...
├── data_visualization/        # TV2 – phân tích và hàm vẽ biểu đồ
│   ├── data_analysis.py       # hàm vẽ dùng lại trong demo
│   └── output/                # biểu đồ HTML, findings.txt
├── demo/                      # TV3 – ứng dụng Streamlit nhiều trang
│   ├── app.py                 # khởi động: điều hướng, bộ lọc dùng chung
│   ├── views/                 # 7 trang: overview, profile, compare, matcher, analysis, jobs_search, about
│   ├── state.py               # nạp dữ liệu + bộ nhớ đệm theo bộ lọc
│   ├── data_utils.py          # lọc dữ liệu, tính chỉ tiêu, điểm gợi ý nghề
│   ├── charts.py              # hệ màu chung + biểu đồ (gọi lại hàm của TV2)
│   ├── ui.py                  # CSS, thẻ chỉ số, chú thích nguồn/đơn vị/n
│   ├── data/nganh_hoc_lien_quan.csv   # nhóm nghề – ngành học – thẻ sở thích
│   └── tests/test_data_utils.py
├── .streamlit/config.toml
├── requirements.txt
└── requirements-dev.txt
```

## Chạy demo

Yêu cầu: **Python 3.10 trở lên** và Git. Đã chạy thử với Python 3.13, Streamlit 1.66, Plotly 7.1.

### 1. Tải code

```bash
git clone https://github.com/ttien2312/viet-career-insights.git
cd viet-career-insights
```

### 2. Tạo môi trường ảo và cài thư viện

Windows (PowerShell hoặc CMD):

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Chạy ứng dụng

Chạy **từ thư mục gốc của repo**:

```bash
streamlit run demo/app.py
```

Trình duyệt tự mở `http://localhost:8501`. Lần đầu mất khoảng 5–10 giây để đọc dữ liệu; sau đó dữ liệu được lưu cache nên thao tác lọc gần như tức thì. Dừng ứng dụng bằng `Ctrl + C` trong cửa sổ dòng lệnh.

## Tính năng

| Trang | Nội dung |
|---|---|
| Tổng quan | 5 thẻ chỉ số, nhận xét tự động, **bản đồ cơ hội nghề nghiệp** (lương khởi điểm × % tin cho người mới × số tin), xếp hạng nhóm nghề theo 5 chỉ tiêu, mức tập trung việc làm theo địa điểm. Bấm vào bong bóng/thanh để mở hồ sơ nghề. |
| Hồ sơ nghề | Thẻ chỉ số có so sánh với toàn thị trường, thang lương theo kinh nghiệm (P25–trung vị–P75), ngành học gợi ý, trình độ và ngoại ngữ yêu cầu, kỹ năng chuyên môn/mềm, nơi tuyển, vị trí hay gặp. |
| So sánh | 2–3 nhóm nghề, mỗi nhóm một màu cố định: hồ sơ 5 chiều, đường lương theo kinh nghiệm, tỷ trọng kinh nghiệm, ma trận kỹ năng chung/riêng, bảng chi tiết. |
| Gợi ý cho bạn | Chọn sở thích, kéo 5 thanh ưu tiên, chọn nơi làm việc → điểm phù hợp 0–100 cho từng nhóm nghề, thanh màu cho thấy điểm đến từ tiêu chí nào; top 3 kèm ngành học. |
| Phân tích chuyên sâu | Biểu đồ phân tích của TV2 (lương theo nhóm nghề/kinh nghiệm, yêu cầu kinh nghiệm, bản đồ nhiệt kỹ năng) chạy theo bộ lọc. |
| Tra cứu tin | Bảng tin đã lọc, sắp xếp/tìm kiếm, tải CSV. |
| Dữ liệu & phương pháp | Nguồn, cách tính chỉ tiêu, công thức điểm gợi ý, giới hạn dữ liệu, bảng chất lượng. |

Bộ lọc ở thanh bên (nhóm nghề, địa điểm, kinh nghiệm, từ khóa, chỉ tin có lương) dùng chung cho mọi trang. Mọi biểu đồ ghi **nguồn, đơn vị, số mẫu (n)** và có bảng số liệu đi kèm; khi bộ lọc không còn tin nào, ứng dụng hiện thông báo thay vì báo lỗi.

Hệ màu: một chuỗi = xanh; so sánh = xanh/cam/xanh ngọc (đã kiểm tra phân biệt được với người mù màu); đại lượng có thứ tự = một tông xanh nhạt → đậm. Số viết kiểu Việt Nam (47.564; 13,5).

## Dữ liệu và chỉ tiêu

- Demo đọc trực tiếp đầu ra của TV1: `data_preprocessing/data/jobs_clean.csv.gz` và `skills_table.csv` — cùng phiên bản với báo cáo và slide.
- Biểu đồ chính gọi lại hàm trong `data_visualization/data_analysis.py` (TV2), chỉ chỉnh trục/tiêu đề để vẫn đúng khi dữ liệu đã lọc.
- Lương = `salary_for_analysis` (trung điểm khoảng lương, triệu VND/tháng). Tin "Thỏa thuận" không có trong biểu đồ lương.

### Cập nhật bảng ngành học (TV4)

Thay nội dung `demo/data/nganh_hoc_lien_quan.csv`, giữ cột đầu tiên là **`category_clean`** (đúng tên 16 nhóm nghề). Cột `nganh_hoc_goi_y`, `huong_cao_dang_trung_cap` ngăn các mục bằng dấu `;`; cột `so_thich` là thẻ sở thích dùng ở trang Gợi ý. Bản hiện tại là bản nháp của TV3, cần đối chiếu với nguồn chính thức.

## Kiểm thử

```bash
pip install -r requirements-dev.txt
pytest demo/tests -q
```

Bộ kiểm thử (17 ca) kiểm tra: số dòng khớp bảng chất lượng của TV1, lọc theo từng tiêu chí và kết hợp, tin có nhiều địa điểm, **bộ lọc cho kết quả rỗng**, chỉ tiêu toàn bộ dữ liệu khớp `findings.txt` của TV2, bảng ngành học phủ đủ 16 nhóm nghề, định dạng số kiểu Việt Nam, và điểm gợi ý bằng đúng tổng các phần đóng góp.

Danh sách kiểm thử thủ công khi chạy trên máy khác: xem phần báo cáo TV3.

## Lỗi thường gặp

| Hiện tượng | Cách xử lý |
|---|---|
| `streamlit: command not found` / không nhận lệnh | Chưa kích hoạt môi trường ảo, hoặc dùng `python -m streamlit run demo/app.py`. |
| `Không tìm thấy tệp dữ liệu` | Chạy lệnh từ thư mục gốc repo; kiểm tra đã có `data_preprocessing/data/jobs_clean.csv.gz` (repo phải được clone đủ, không tải thiếu tệp). |
| `ModuleNotFoundError: data_analysis` | Thiếu thư mục `data_visualization/` hoặc chạy từ bản copy chỉ có thư mục `demo/`. |
| Cổng 8501 đang bận | `streamlit run demo/app.py --server.port 8502` |
| Windows báo lỗi khi kích hoạt `.venv` trong PowerShell | Chạy `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` rồi thử lại, hoặc dùng CMD. |
