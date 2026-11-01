"""Trang 5 – Phân tích chuyên sâu: các biểu đồ phân tích của TV2 trên dữ liệu đã lọc."""

import streamlit as st

import charts
import data_utils as du
import state
import ui


def render():
    f = state.current()
    jobs = state.jobs(f)
    _, skills, _ = state.load()
    ui.hero("Phân tích chuyên sâu", "Các biểu đồ phân tích của nhóm, tương tác theo bộ lọc",
            "Dùng lại đúng hàm vẽ trong data_visualization/data_analysis.py (TV2), áp cùng hệ màu của demo.")
    ui.filter_chips(f)
    if jobs.empty:
        ui.empty_state()
        return
    n_sal = int(jobs["salary_for_analysis"].notna().sum())
    t1, t2, t3, t4 = st.tabs(["Lương theo nhóm nghề", "Lương theo kinh nghiệm", "Yêu cầu kinh nghiệm", "Kỹ năng"])
    with t1:
        if n_sal == 0:
            st.info("Các tin khớp bộ lọc không công khai lương dạng số.")
        else:
            st.markdown("Hộp chứa 50% tin ở giữa, vạch trong hộp là **trung vị**; râu kéo tới giá trị thường gặp xa nhất.")
            ui.chart(charts.tv2_salary_by_industry, jobs, key="an_sal_ind", n=n_sal,
                     unit="triệu VND/tháng (trung điểm khoảng lương)", extra="Trục cắt ở 40 triệu để dễ đọc.")
    with t2:
        if n_sal == 0:
            st.info("Các tin khớp bộ lọc không công khai lương dạng số.")
        else:
            ui.chart(charts.tv2_salary_by_experience, jobs, key="an_sal_exp", n=n_sal,
                     unit="triệu VND/tháng (trung điểm khoảng lương)",
                     table=du.salary_ladder(jobs).round(1))
    with t3:
        ui.chart(charts.tv2_experience_by_industry, jobs, key="an_exp", n=len(jobs), unit="% số tin của nhóm nghề")
    with t4:
        fs = du.filter_skills(skills, jobs)
        c1, c2 = st.columns(2, gap="large")
        with c1:
            t = state.top_skills(f, None, du.TECH, 12)
            ui.chart(charts.skills_bar, t, charts.BLUE, "Top kỹ năng chuyên môn", key="an_tech", n=len(jobs),
                     unit="% số tin", table=t.round(1))
        with c2:
            t = state.top_skills(f, None, du.SOFT, 12)
            ui.chart(charts.skills_bar, t, charts.ORANGE, "Top kỹ năng mềm", key="an_soft", n=len(jobs),
                     unit="% số tin", table=t.round(1))
        if not fs.empty:
            ui.chart(charts.tv2_skill_heatmap, fs, jobs, key="an_heat", n=len(jobs),
                     unit="% số tin của nhóm nghề có nhắc tới kỹ năng")
        st.caption("Kỹ năng được trích từ nội dung tin; một số kỹ năng còn nhiều cách ghi (VD: “AutoCAD”/“Autocad”).")
