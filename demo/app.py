"""
Viet Career Insights – demo tương tác của Nhóm 15 (môn Trực quan hóa thông tin).
Đề tài: tư vấn chọn ngành cho học sinh THPT dựa trên thị trường lao động Việt Nam (VietJobs).

Chạy từ thư mục gốc của repo:
    streamlit run demo/app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import data_utils as du  # noqa: E402
import state  # noqa: E402
import ui  # noqa: E402
from views import about, analysis, compare, jobs_search, matcher, overview, profile  # noqa: E402

st.set_page_config(page_title="Viet Career Insights – Nhóm 15", page_icon=":material/school:",
                   layout="wide", initial_sidebar_state="expanded")
ui.inject_css()

try:
    JOBS, _, LOCS = state.load()
except FileNotFoundError as exc:
    st.error(f"Không tìm thấy tệp dữ liệu: {exc.filename}. Hãy chạy lệnh từ thư mục gốc của repo "
             "và kiểm tra thư mục data_preprocessing/data.")
    st.stop()

# ----------------------------------------------------------------------------
# Các trang
# ----------------------------------------------------------------------------
pages = {
    "overview": st.Page(overview.render, title="Tổng quan", icon=":material/insights:", url_path="tong-quan", default=True),
    "profile": st.Page(profile.render, title="Hồ sơ nghề", icon=":material/badge:", url_path="ho-so-nghe"),
    "compare": st.Page(compare.render, title="So sánh", icon=":material/compare_arrows:", url_path="so-sanh"),
    "matcher": st.Page(matcher.render, title="Gợi ý cho bạn", icon=":material/explore:", url_path="goi-y"),
    "analysis": st.Page(analysis.render, title="Phân tích chuyên sâu", icon=":material/query_stats:", url_path="phan-tich"),
    "jobs": st.Page(jobs_search.render, title="Tra cứu tin", icon=":material/search:", url_path="tra-cuu"),
    "about": st.Page(about.render, title="Dữ liệu & phương pháp", icon=":material/info:", url_path="phuong-phap"),
}
state.PAGES.update(pages)
nav = st.navigation(list(pages.values()), position="top")

# ----------------------------------------------------------------------------
# Thanh bên: bộ lọc dùng chung
# ----------------------------------------------------------------------------
state.init_filters()
categories = JOBS["category_clean"].value_counts().index.tolist()
loc_counts = LOCS.value_counts()
loc_options = loc_counts.index.tolist()

with st.sidebar:
    st.markdown("### Bộ lọc")
    st.caption("Áp dụng cho mọi trang. Để trống một ô = lấy tất cả.")
    st.multiselect("Nhóm nghề", categories, key="f_cat", placeholder="Tất cả nhóm nghề",
                   help="Trang Hồ sơ nghề, So sánh và Gợi ý có ô chọn nhóm nghề riêng.")
    st.multiselect("Địa điểm", loc_options, key="f_loc", placeholder="Tất cả địa điểm",
                   format_func=lambda x: f"{x} ({du.fmt_int(loc_counts.get(x, 0))})")
    st.multiselect("Kinh nghiệm yêu cầu", du.EXPERIENCE_ORDER, key="f_exp", placeholder="Mọi mức kinh nghiệm")
    st.text_input("Từ khóa trong tên vị trí", key="f_kw", placeholder="VD: kế toán, data, sale")
    st.toggle("Chỉ tin có công khai lương", key="f_salary")
    st.button("Xóa bộ lọc", on_click=state.reset_filters, icon=":material/restart_alt:", width="stretch")

    f = state.current()
    n_now = len(state.jobs(f))
    st.divider()
    st.metric("Số tin đang xem", du.fmt_int(n_now), help=f"Trên tổng {du.fmt_int(len(JOBS))} tin")
    st.progress(min(1.0, n_now / len(JOBS)), text=f"{du.fmt_pct(n_now / len(JOBS) * 100, 1)} toàn bộ dữ liệu")
    st.caption(f"{ui.SOURCE}. {du.fmt_int(len(JOBS))} tin tuyển dụng tại Việt Nam.")

nav.run()
