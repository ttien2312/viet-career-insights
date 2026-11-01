"""Trang 1 – Tổng quan thị trường."""

import streamlit as st

import charts
import data_utils as du
import state
import ui


def _clicked_category(event, stats) -> str | None:
    """Lấy nhóm nghề từ điểm người dùng bấm trên biểu đồ (customdata[0])."""
    try:
        pts = event.selection.points if event else []
    except AttributeError:
        return None
    for p in pts:
        cd = p.get("customdata")
        if cd:
            return cd[0]
    return None


def render():
    f = state.current()
    jobs = state.jobs(f)
    _, _, locs = state.load()
    _, _, findings = state.static()

    ui.hero("Viet Career Insights · Nhóm 15",
            f"Thị trường lao động Việt Nam qua {du.fmt_int(len(state.load()[0]))} tin tuyển dụng",
            "Công cụ giúp học sinh THPT xem nghề nào đang cần người, lương khởi điểm bao nhiêu, "
            "cần kỹ năng gì và nên học ngành nào – từ dữ liệu tuyển dụng thật của VietJobs.")
    st.markdown("""<div class='vci-steps'>
      <div class='vci-step'><b>1. Nhìn bức tranh chung</b><br>Ma trận cơ hội và xếp hạng ở trang này.</div>
      <div class='vci-step'><b>2. Tìm hiểu một nghề</b><br>Bấm vào một bong bóng hoặc mở <i>Hồ sơ nghề</i>.</div>
      <div class='vci-step'><b>3. Đặt các lựa chọn cạnh nhau</b><br>Trang <i>So sánh</i> cho 2–3 nhóm nghề.</div>
      <div class='vci-step'><b>4. Nhận gợi ý riêng</b><br>Trang <i>Gợi ý cho bạn</i> theo sở thích và ưu tiên.</div>
    </div>""", unsafe_allow_html=True)
    ui.filter_chips(f)

    if jobs.empty:
        ui.empty_state()
        return

    s = state.summary(f)
    stats = state.stats(f)
    conc = du.concentration(jobs, locs)
    hn_hcm = conc.loc[conc["Nhóm"] != "Tỉnh, thành khác", "% tin"].sum() if not conc.empty else float("nan")
    ui.kpis([
        {"label": "Tin tuyển dụng", "value": du.fmt_int(s["n"]),
         "sub": f"{du.fmt_int(len(stats))} nhóm nghề"},
        {"label": "Lương trung vị", "value": du.fmt_dec(s["median"]), "unit": "triệu",
         "sub": f"50% tin trong khoảng {du.fmt_dec(s['p25'])}–{du.fmt_dec(s['p75'])} tr"},
        {"label": "Lương khởi điểm (người mới)", "value": du.fmt_dec(s["entry_salary"]), "unit": "triệu",
         "sub": f"trung vị {du.fmt_int(s['entry_salary_n'])} tin cho người mới"},
        {"label": "Tin nhận người chưa / dưới 1 năm kinh nghiệm", "value": du.fmt_pct(s["entry_pct"]),
         "sub": "cơ hội cho sinh viên mới ra trường"},
        {"label": "Tin ở Hà Nội hoặc TP. HCM", "value": du.fmt_pct(hn_hcm),
         "sub": f"{du.fmt_pct(s['negotiable_pct'])} tin ghi lương “thỏa thuận”"},
    ])

    ui.insight(du.market_insights(stats, s, conc))

    # --- Ma trận cơ hội -------------------------------------------------------
    ui.section("Bản đồ cơ hội nghề nghiệp",
               "Mỗi bong bóng là một nhóm nghề: càng sang phải lương khởi điểm càng cao, càng lên trên càng "
               "nhiều tin nhận người mới, bong bóng càng to càng nhiều việc làm. "
               "<b>Bấm vào một bong bóng để mở hồ sơ nghề đó.</b>")
    hl = list(f["cat"]) or None
    tbl = stats[stats["category_clean"] != du.OTHER_CATEGORY][
        ["category_clean", "n", "entry_salary", "entry_salary_n", "entry_pct", "median"]].rename(columns={
            "category_clean": "Nhóm nghề", "n": "Số tin", "entry_salary": "Lương khởi điểm (tr)",
            "entry_salary_n": "Số tin có lương (người mới)", "entry_pct": "% tin cho người mới",
            "median": "Lương trung vị (tr)"}).round(1)
    ev = ui.chart(charts.opportunity_matrix, stats, s, hl, key="ov_matrix", n=s["n"],
                  unit="triệu VND/tháng; % số tin",
                  extra="Đường xám = mức toàn thị trường. Không vẽ “Nhóm nghề khác” và nhóm có dưới 10 tin có lương cho người mới.",
                  table=tbl, select=True)
    picked = _clicked_category(ev, stats)
    if picked:
        state.go_profile(picked)

    # --- Xếp hạng -----------------------------------------------------------
    ui.section("Xếp hạng nhóm nghề", "Chọn chỉ tiêu để xếp hạng lại; bấm vào một thanh để mở hồ sơ nghề.")
    metric = st.segmented_control("Xếp theo", list(charts.RANK_METRICS), default="Số tin tuyển dụng",
                                  key="ov_metric", label_visibility="collapsed") or "Số tin tuyển dụng"
    col, _, unit = charts.RANK_METRICS[metric]
    ev2 = ui.chart(charts.ranked_bar, stats, metric, hl, key="ov_rank", n=s["n"], unit=unit,
                   extra="Lương: trung điểm khoảng lương trong tin; ô có dưới 10 tin có lương được bỏ qua. Không xếp hạng “Nhóm nghề khác”.",
                   select=True)
    picked = _clicked_category(ev2, stats)
    if picked:
        state.go_profile(picked)

    # --- Địa điểm -----------------------------------------------------------
    ui.section("Việc làm tập trung ở đâu?",
               "Thanh trên chia mỗi tin vào đúng một nhóm; biểu đồ dưới đếm theo từng nơi được ghi trong tin.")
    ui.chart(charts.concentration_bar, conc, key="ov_conc", n=len(jobs), unit="% số tin", table=conc.round(1))
    loc = du.location_counts(jobs, locs, 10)
    ui.chart(charts.location_bar, loc, key="ov_loc", n=len(jobs), unit="số tin",
             extra="Một tin có thể ghi nhiều địa điểm nên tổng các thanh có thể lớn hơn n.")

    if findings:
        with st.expander("Phát hiện chính trên toàn bộ dữ liệu (phân tích của TV2)"):
            for x in findings:
                st.markdown(f"- {x}")
