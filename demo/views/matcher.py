"""Trang 4 – Gợi ý nhóm nghề theo sở thích và ưu tiên của học sinh."""

import streamlit as st

import charts
import data_utils as du
import state
import ui


def render():
    _, majors, _ = state.static()
    _, _, locs = state.load()
    tags = du.interest_tags(majors)
    tag_list = du.all_tags(majors)

    ui.hero("Gợi ý cho bạn", "Nhóm nghề nào hợp với bạn?",
            "Chọn điều bạn thích và điều bạn coi trọng. Điểm được tính minh bạch từ dữ liệu tuyển dụng – "
            "mỗi màu trong thanh cho biết phần điểm đến từ tiêu chí nào.")

    left, right = st.columns([1, 2], gap="large")
    with left:
        with st.container(border=True):
            st.markdown("**1. Bạn thích / giỏi điều gì?**")
            for k, v in {"m_tags": [], "m_w_interest": 5, "m_w_salary": 3, "m_w_demand": 3,
                         "m_w_entry": 3, "m_w_growth": 2, "m_loc": "Toàn quốc"}.items():
                state.keep(k, v)
            chosen = st.pills("Sở thích", tag_list, selection_mode="multi", key="m_tags",
                              label_visibility="collapsed")
            st.markdown("**2. Bạn coi trọng điều gì?** (0 = không quan tâm, 5 = rất quan trọng)")
            w = {
                "interest": st.slider("Hợp sở thích", 0, 5, key="m_w_interest"),
                "entry_salary": st.slider("Lương khởi điểm cao", 0, 5, key="m_w_salary"),
                "demand": st.slider("Nhiều cơ hội việc làm", 0, 5, key="m_w_demand"),
                "entry_pct": st.slider("Dễ vào nghề khi chưa có kinh nghiệm", 0, 5, key="m_w_entry"),
                "growth": st.slider("Lương tăng nhanh theo kinh nghiệm", 0, 5, key="m_w_growth"),
            }
            st.markdown("**3. Bạn muốn làm việc ở đâu?**")
            top_locs = locs.value_counts().head(25).index.tolist()
            where = st.selectbox("Nơi làm việc", ["Toàn quốc"] + top_locs, key="m_loc",
                                 label_visibility="collapsed")
            for k in ["m_tags", "m_w_interest", "m_w_salary", "m_w_demand", "m_w_entry", "m_w_growth", "m_loc"]:
                state.remember(k)

    nat_stats = state.national_stats()
    if where == "Toàn quốc":
        local = nat_stats
    else:
        f_loc = dict(state.NATIONAL, loc=(where,))
        local = state.stats(f_loc)
    scores = du.match_scores(nat_stats, local, tags, chosen or [], w)

    with right:
        if sum(w.values()) == 0:
            st.info("Hãy kéo ít nhất một thanh trượt lên trên 0.")
            return
        if not chosen and w["interest"] > 0:
            st.caption("Chưa chọn sở thích nào – điểm hiện chỉ dựa trên các ưu tiên còn lại.")
        top3 = scores.head(3)
        cols = st.columns(3)
        m = majors.set_index("category_clean")
        for i, (col, (_, r)) in enumerate(zip(cols, top3.iterrows())):
            with col:
                with st.container(border=True):
                    st.markdown(f"<div class='vci-rank'>#{i + 1}</div><b>{r['category_clean']}</b>",
                                unsafe_allow_html=True)
                    st.metric("Điểm phù hợp", f"{r['score']:.0f}/100")
                    ns = nat_stats.set_index("category_clean").loc[r["category_clean"]]
                    st.caption(f"Khởi điểm {du.fmt_dec(ns['entry_salary'])} tr · "
                               f"{du.fmt_pct(ns['entry_pct'])} tin cho người mới · "
                               f"{du.fmt_int(r['n_local'])} tin{'' if where == 'Toàn quốc' else ' ở ' + where}")
                    if r["category_clean"] in m.index:
                        majors_txt = str(m.loc[r["category_clean"]].get("nganh_hoc_goi_y", "")).split(";")[:3]
                        st.caption("Ngành học: " + ", ".join(x.strip() for x in majors_txt))
                    if st.button("Xem hồ sơ nghề", key=f"m_go_{i}", icon=":material/arrow_forward:", width="stretch"):
                        state.go_profile(r["category_clean"])

        ui.section("Bảng điểm của tất cả nhóm nghề")
        labels = du.CRITERIA
        tbl = scores[["category_clean", "score", *labels.keys(), "n_local"]].rename(
            columns={"category_clean": "Nhóm nghề", "score": "Điểm", "n_local": "Số tin", **labels}).round(1)
        ui.chart(charts.match_bars, scores, labels, key="m_bars", n=int(scores["n_local"].sum()),
                 unit="điểm (0–100)",
                 extra="Lương và mức tăng lương lấy toàn quốc để đủ mẫu; số tin và % cho người mới lấy theo nơi bạn chọn.",
                 table=tbl)
    st.info("Đây là gợi ý từ dữ liệu tin tuyển dụng, không thay thế tư vấn của thầy cô, gia đình hay "
            "chuyên gia hướng nghiệp. Hãy dùng kết quả để biết nên tìm hiểu kỹ nghề nào trước.",
            icon=":material/lightbulb:")
