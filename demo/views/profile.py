"""Trang 2 – Hồ sơ một nhóm nghề."""

import numpy as np
import streamlit as st

import charts
import data_utils as du
import state
import ui


def render():
    f = state.current()
    jobs_all = state.jobs(f, with_cat=False)
    _, _, locs = state.load()
    _, majors, _ = state.static()
    nat = state.national_stats()
    cats = nat["category_clean"].tolist()

    state.keep("profile_cat", "Công nghệ thông tin" if "Công nghệ thông tin" in cats else cats[0])
    if st.session_state["profile_cat"] not in cats:
        st.session_state["profile_cat"] = cats[0]

    ui.hero("Hồ sơ nghề", "Một nhóm nghề trông như thế nào trên thị trường?",
            "Số việc làm, lương theo từng mức kinh nghiệm, kỹ năng nhà tuyển dụng cần và ngành học nên chọn.")
    cat = st.selectbox("Chọn nhóm nghề", cats, key="profile_cat",
                       format_func=lambda c: f"{c}  ·  {du.fmt_int(nat.set_index('category_clean').loc[c, 'n'])} tin")
    state.remember("profile_cat")
    ui.filter_chips(f, applies="no_cat")

    d = jobs_all[jobs_all["category_clean"] == cat]
    if d.empty:
        ui.empty_state("cho nhóm nghề này")
        return
    stats = state.stats(f, with_cat=False)
    row = stats.set_index("category_clean").loc[cat].to_dict() | {"category_clean": cat}
    mkt = state.summary(f, with_cat=False)

    def delta(a, b):
        return a - b if not (np.isnan(a) or np.isnan(b)) else None

    ui.kpis([
        {"label": "Tin tuyển dụng", "value": du.fmt_int(row["n"]),
         "sub": f"{du.fmt_pct(row['share'], 1)} toàn thị trường"},
        {"label": "Lương trung vị", "value": du.fmt_dec(row["median"]), "unit": "triệu",
         "delta": delta(row["median"], mkt["median"]),
         "delta_text": du.fmt_dec(abs(delta(row["median"], mkt["median"]) or 0)) + " tr", "sub": "so với toàn thị trường"},
        {"label": "Lương khởi điểm", "value": du.fmt_dec(row["entry_salary"]), "unit": "triệu",
         "delta": delta(row["entry_salary"], mkt["entry_salary"]),
         "delta_text": du.fmt_dec(abs(delta(row["entry_salary"], mkt["entry_salary"]) or 0)) + " tr",
         "sub": "so với toàn thị trường"},
        {"label": "Tin cho người mới", "value": du.fmt_pct(row["entry_pct"]),
         "delta": delta(row["entry_pct"], mkt["entry_pct"]),
         "delta_text": du.fmt_dec(abs(delta(row["entry_pct"], mkt["entry_pct"]) or 0), 0) + " điểm %",
         "sub": "so với toàn thị trường"},
        {"label": "Lương khi có 3+ năm kinh nghiệm", "value": du.fmt_dec(row["senior_salary"]), "unit": "triệu",
         "sub": f"gấp {du.fmt_dec(row['growth'])} lần người mới" if not np.isnan(row["growth"]) else "chưa đủ mẫu"},
    ])
    ui.insight(du.profile_insights(cat, row, mkt, stats))

    left, right = st.columns([3, 2], gap="large")
    with left:
        ui.section("Lương tăng thế nào theo kinh nghiệm?",
                   "Thanh xanh nhạt: 50% tin ở giữa; chấm xanh đậm: trung vị của nghề; đường xám: toàn thị trường.")
        lad = du.salary_ladder(d)
        mkt_lad = du.salary_ladder(jobs_all)
        ui.chart(charts.salary_ladder, lad, mkt_lad, du.short(cat), key="pf_ladder",
                 n=int(d["salary_for_analysis"].notna().sum()), unit="triệu VND/tháng",
                 extra="Mức có dưới 10 tin có lương được bỏ trống.",
                 table=lad.rename(columns={"n": "Số tin có lương", "p25": "P25", "median": "Trung vị", "p75": "P75"}).round(1))
    with right:
        ui.section("Học gì để làm nghề này?")
        m = majors.set_index("category_clean")
        if cat in m.index:
            st.markdown("**Ngành đại học gợi ý**")
            ui.tags(str(m.loc[cat].get("nganh_hoc_goi_y", "")).split(";"))
            hc = str(m.loc[cat].get("huong_cao_dang_trung_cap", ""))
            if hc:
                st.markdown("**Hướng cao đẳng / trung cấp**")
                ui.tags(hc.split(";"))
        st.markdown("**Trình độ nhà tuyển dụng nhắc tới**")
        c1, c2 = st.columns(2)
        c1.metric("Đại học", du.fmt_pct(row["univ_pct"]), help="% tin có nhắc tới bằng Đại học")
        c2.metric("Cao đẳng / Trung cấp", du.fmt_pct(row["college_pct"]),
                  help="% tin có nhắc tới Cao đẳng hoặc Trung cấp (một tin có thể nhắc nhiều mức)")
        lang = du.languages_table(d)
        if not lang.empty:
            st.markdown("**Ngoại ngữ hay được yêu cầu**")
            ui.tags([f"{r['Ngoại ngữ']} · {du.fmt_pct(r['% tin'])}" for _, r in lang.iterrows()])
        st.caption("Bảng ngành học: bản nháp của nhóm, cần đối chiếu nguồn chính thức.")

    ui.section("Nhà tuyển dụng cần kỹ năng gì?", "% số tin của nhóm nghề có nhắc tới kỹ năng.")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        t = state.top_skills(f, cat, du.TECH, 10, with_cat=False)
        ui.chart(charts.skills_bar, t, charts.BLUE, "Kỹ năng chuyên môn", key="pf_tech", n=len(d),
                 unit="% số tin", table=t.round(1))
    with c2:
        t = state.top_skills(f, cat, du.SOFT, 10, with_cat=False)
        ui.chart(charts.skills_bar, t, charts.ORANGE, "Kỹ năng mềm", key="pf_soft", n=len(d),
                 unit="% số tin", table=t.round(1))

    c1, c2 = st.columns(2, gap="large")
    with c1:
        ui.section("Tuyển ở đâu?")
        loc = du.location_counts(d, locs, 8)
        ui.chart(charts.location_bar, loc, key="pf_loc", n=len(d), unit="số tin")
    with c2:
        ui.section("Vị trí hay gặp")
        ex = du.title_examples(d, 10)
        st.dataframe(ex, hide_index=True, key="pf_titles", height=min(420, 36 * len(ex) + 40),
                     column_config={"Vị trí": st.column_config.TextColumn(width="medium"),
                                    "Lương trung vị (triệu)": st.column_config.NumberColumn("Lương TV (tr)", format="%.1f", width="small"),
                                    "Số tin": st.column_config.ProgressColumn(
                                        format="%d", width="small", min_value=0,
                                        max_value=int(ex["Số tin"].max()) if len(ex) else 1)})
        st.caption(f"{ui.SOURCE} · n = {du.fmt_int(len(d))} tin")

    st.page_link(state.PAGES["compare"], label="So sánh nhóm nghề này với nghề khác", icon=":material/compare_arrows:")
