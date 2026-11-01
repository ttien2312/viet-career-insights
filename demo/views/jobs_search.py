"""Trang 6 – Tra cứu tin tuyển dụng."""

import streamlit as st

import data_utils as du
import state
import ui


def render():
    f = state.current()
    jobs = state.jobs(f)
    ui.hero("Tra cứu tin", "Xem từng tin tuyển dụng cụ thể",
            "Bảng theo bộ lọc ở thanh bên; bấm tiêu đề cột để sắp xếp, dùng ô tìm kiếm của bảng để tìm nhanh.")
    ui.filter_chips(f)
    if jobs.empty:
        ui.empty_state()
        return
    tbl = du.jobs_table(jobs)
    c1, c2, c3 = st.columns(3)
    c1.metric("Số tin", du.fmt_int(len(tbl)))
    c2.metric("Có công khai lương", du.fmt_pct(tbl["Lương (triệu/tháng)"].notna().mean() * 100))
    c3.metric("Lương trung vị", du.fmt_dec(tbl["Lương (triệu/tháng)"].median(), 1, " tr"))
    mx = float(tbl["Lương (triệu/tháng)"].quantile(0.99)) if tbl["Lương (triệu/tháng)"].notna().any() else 50.0
    st.dataframe(tbl, hide_index=True, key="jobs_table", height=560,
                 column_config={
                     "Vị trí": st.column_config.TextColumn(width="large"),
                     "Lương (triệu/tháng)": st.column_config.ProgressColumn(
                         format="%.1f", min_value=0.0, max_value=max(mx, 1.0)),
                 })
    st.download_button("Tải danh sách (CSV)", tbl.to_csv(index=False).encode("utf-8-sig"),
                       file_name="tin_tuyen_dung_da_loc.csv", mime="text/csv", icon=":material/download:")
    st.caption(f"{ui.SOURCE}. Lương: trung điểm khoảng lương trong tin (triệu VND/tháng); trống = không công khai.")
