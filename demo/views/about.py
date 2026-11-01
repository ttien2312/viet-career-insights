"""Trang 7 – Dữ liệu, cách tính chỉ tiêu và giới hạn."""

import streamlit as st

import data_utils as du
import state
import ui


def render():
    jobs, _, _ = state.load()
    quality, _, _ = state.static()
    no_sal = int(jobs["salary_for_analysis"].isna().sum())
    ui.hero("Dữ liệu & phương pháp", "Số liệu này tin được đến đâu?",
            "Nguồn, cách tính từng chỉ tiêu, công thức gợi ý nghề và những giới hạn cần biết khi tư vấn.")

    ui.section("Nguồn dữ liệu")
    st.markdown(f"""
Bộ tin tuyển dụng **VietJobs**, đã được nhóm làm sạch: lọc phạm vi Việt Nam, bỏ dòng trùng, chuẩn hóa địa điểm,
kinh nghiệm, kỹ năng và lương. Demo đọc trực tiếp `data_preprocessing/data/jobs_clean.csv.gz` và
`skills_table.csv` – cùng phiên bản với báo cáo và slide. Tổng số tin: **{du.fmt_int(len(jobs))}**.
""")
    ui.section("Cách tính chỉ tiêu")
    st.markdown("""
| Chỉ tiêu | Cách tính |
|---|---|
| Lương | Trung điểm khoảng lương ghi trong tin (triệu VND/tháng). Chỉ tính tin có lương dạng số. |
| Lương trung vị | Mức ở giữa khi xếp các tin theo lương – ít bị kéo lệch bởi vài tin lương rất cao. |
| Khoảng P25–P75 | 50% tin ở giữa; cho biết mức lương “thường gặp”. |
| Lương khởi điểm | Trung vị lương của tin yêu cầu *không có* hoặc *dưới 1 năm* kinh nghiệm. |
| Tin cho người mới | % tin yêu cầu không có hoặc dưới 1 năm kinh nghiệm. |
| Tăng lương theo kinh nghiệm | Trung vị lương tin yêu cầu từ 3 năm ÷ lương khởi điểm. |
| % tin nhắc Đại học | % tin có nhắc tới bằng Đại học trong phần yêu cầu (một tin có thể nhắc nhiều mức). |
| Kỹ năng | % số tin có nhắc tới kỹ năng đó. |

Ô nào có **dưới 10 tin có lương** thì không tính trung vị, để tránh kết luận từ mẫu quá nhỏ.
""")
    ui.section("Công thức điểm gợi ý (trang Gợi ý cho bạn)")
    st.markdown("Mỗi tiêu chí được đưa về thang 0–1 giữa 15 nhóm nghề (giá trị thấp nhất = 0, cao nhất = 1):")
    st.latex(r"\tilde{x}_{k} = \frac{x_{k} - \min(x)}{\max(x) - \min(x)}")
    st.markdown("Điểm là trung bình có trọng số theo các thanh trượt bạn chọn (trọng số 0–5):")
    st.latex(r"\text{Điểm} = 100 \times \frac{\sum_{i} w_i \, \tilde{x}_{i}}{\sum_{i} w_i}")
    st.markdown("""
Ví dụ: chỉ bật *Lương khởi điểm* (trọng số 3) và *Dễ vào nghề* (trọng số 1). Một nghề có lương khởi điểm cao nhất
(giá trị 1,0) và tỷ lệ tin cho người mới ở giữa (0,5) được 100 × (3×1,0 + 1×0,5) / 4 = **87,5 điểm**.

- *Hợp sở thích* = số sở thích bạn chọn có trong nghề đó ÷ số sở thích đã chọn.
- *Nhiều việc làm* dùng thang log của số tin để vài nhóm rất lớn không lấn át.
- Mỗi màu trên thanh điểm là phần đóng góp của một tiêu chí; cộng lại đúng bằng điểm.
""")
    ui.section("Giới hạn cần lưu ý khi tư vấn")
    st.markdown(f"""
- Tin tuyển dụng phản ánh nhu cầu **đăng tuyển trên một nền tảng**, không phải toàn bộ thị trường lao động.
- {du.fmt_int(no_sal)} tin ({du.fmt_pct(no_sal / len(jobs) * 100)}) không có lương dạng số; lương trong tin là mức
  doanh nghiệp đăng, không phải thu nhập thực nhận.
- Một số địa điểm còn ở cấp quận/huyện (VD: “Quận 1”, “Tân Bình”), nên số liệu theo tỉnh có thể thấp hơn thực tế.
- Kỹ năng ghi tự do nên còn từ đồng nghĩa chưa gộp.
- Bảng ngành học và thẻ sở thích là bản nháp của nhóm, cần đối chiếu nguồn chính thức.
""")
    ui.section("Chất lượng dữ liệu trước và sau xử lý")
    q = quality.copy()
    for c in q.columns[1:]:
        q[c] = q[c].map(du.fmt_int)  # chuỗi thống nhất: 48.092; ô trống = "—"
    st.dataframe(q, hide_index=True, key="quality_table")
    st.caption("Nhóm 15 – Trực quan hóa thông tin, HKI 2026–2027. Demo: Streamlit + Plotly.")
