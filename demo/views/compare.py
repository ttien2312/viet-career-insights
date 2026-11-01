"""Trang 3 – So sánh 2–3 nhóm nghề."""

import pandas as pd
import streamlit as st

import charts
import data_utils as du
import state
import ui

DEFAULT = ["Công nghệ thông tin", "Marketing - Truyền thông", "Tài chính - Kế toán - Ngân hàng"]


def render():
    f = state.current()
    base = state.jobs(f, with_cat=False)
    nat = state.national_stats()
    cats_all = nat["category_clean"].tolist()

    ui.hero("So sánh", "Đặt 2–3 nhóm nghề cạnh nhau",
            "Mỗi nhóm nghề giữ nguyên một màu trên mọi biểu đồ của trang. "
            "Bộ lọc địa điểm, kinh nghiệm, từ khóa ở thanh bên vẫn được áp dụng.")
    state.keep("cmp_cats", [c for c in DEFAULT if c in cats_all][:3])
    cats = st.multiselect("Nhóm nghề cần so sánh (tối đa 3)", cats_all, key="cmp_cats", max_selections=3,
                          format_func=du.short)
    state.remember("cmp_cats")
    ui.filter_chips(f, applies="no_cat")
    if len(cats) < 2:
        st.info("Hãy chọn ít nhất 2 nhóm nghề để so sánh.")
        return
    sub = base[base["category_clean"].isin(cats)]
    if sub.empty:
        ui.empty_state()
        return

    # Màu theo vị trí chọn, giữ ổn định khi thêm/bớt nhóm cuối
    colors = {c: charts.SERIES[i] for i, c in enumerate(cats)}
    stats = state.stats(f, with_cat=False)
    st_idx = stats.set_index("category_clean")

    # --- Thẻ tóm tắt từng nghề -------------------------------------------------
    cols = st.columns(len(cats))
    for col, c in zip(cols, cats):
        with col:
            r = st_idx.loc[c] if c in st_idx.index else None
            with st.container(border=True):
                st.markdown(f"<span style='display:inline-block;width:12px;height:12px;border-radius:3px;"
                            f"background:{colors[c]};margin-right:6px'></span><b>{c}</b>", unsafe_allow_html=True)
                if r is None:
                    st.caption("Không có tin với bộ lọc hiện tại.")
                    continue
                a, b = st.columns(2)
                a.metric("Số tin", du.fmt_int(r["n"]))
                b.metric("Lương trung vị", du.fmt_dec(r["median"], 1, " tr"))
                a.metric("Lương khởi điểm", du.fmt_dec(r["entry_salary"], 1, " tr"))
                b.metric("Cho người mới", du.fmt_pct(r["entry_pct"]))

    left, right = st.columns([1, 1], gap="large")
    with left:
        ui.section("Hồ sơ 5 chiều", "Hạng của nhóm nghề trong 15 nhóm trên từng tiêu chí (100 = cao nhất).")
        radar_tbl = st_idx.loc[[c for c in cats if c in st_idx.index],
                               ["n", "median", "entry_salary", "entry_pct", "growth"]].round(2).reset_index()
        radar_tbl.columns = ["Nhóm nghề", "Số tin", "Lương trung vị", "Lương khởi điểm", "% cho người mới", "Tăng lương (lần)"]
        ui.chart(charts.radar, stats, cats, colors, key="cmp_radar", n=len(sub), unit="hạng phần trăm (0–100)",
                 table=radar_tbl)
    with right:
        ui.section("Lương trung vị theo kinh nghiệm", "Độ dốc của đường cho thấy lương tăng nhanh hay chậm khi có thêm kinh nghiệm.")
        ladders = {c: du.salary_ladder(base[base["category_clean"] == c]) for c in cats}
        tbl = pd.concat([lad.assign(**{"Nhóm nghề": c}) for c, lad in ladders.items()])[
            ["Nhóm nghề", "Kinh nghiệm", "n", "p25", "median", "p75"]].round(1)
        ui.chart(charts.compare_ladder, ladders, colors, key="cmp_ladder",
                 n=int(sub["salary_for_analysis"].notna().sum()), unit="triệu VND/tháng",
                 extra="Mức có dưới 10 tin có lương được bỏ trống.", table=tbl)

    ui.section("Nghề nào nhận người mới?", "Tỷ trọng tin theo mức kinh nghiệm yêu cầu, từ nhạt (không yêu cầu) đến đậm (từ 5 năm).")
    dist = du.experience_distribution(base, cats)
    ui.chart(charts.experience_stack, dist, cats, key="cmp_exp", n=len(sub), unit="% số tin của nhóm nghề",
             table=dist.round(1))

    ui.section("Kỹ năng: chung và riêng", "Chấm càng to, kỹ năng càng hay xuất hiện trong tin của nghề đó.")
    tops = {c: state.top_skills(f, c, du.TECH, 8, with_cat=False) for c in cats}
    ui.chart(charts.skills_dot_matrix, tops, colors, key="cmp_skills", n=len(sub), unit="% số tin của nhóm nghề",
             table=pd.concat([t.assign(**{"Nhóm nghề": c}) for c, t in tops.items()]).round(1))

    ui.section("Bảng so sánh chi tiết")
    _, _, locs = state.load()
    skills = state.load()[1]
    st.dataframe(du.compare_table(base, skills, locs, cats).rename(columns=du.short), key="cmp_table")
