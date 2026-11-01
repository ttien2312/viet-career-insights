"""Kiểm thử logic lọc và chỉ tiêu của demo.  Chạy: pytest demo/tests -q"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import data_utils as du  # noqa: E402


@pytest.fixture(scope="module")
def data():
    jobs = du.load_jobs()
    skills = du.load_skills()
    locs = du.explode_locations(jobs)
    return jobs, skills, locs


def test_load_matches_tv1_output(data):
    jobs, skills, _ = data
    quality = du.load_quality()
    after_total = int(quality.loc[quality.iloc[:, 0] == "Tổng số tin tuyển dụng"].iloc[0, 2])
    assert len(jobs) == after_total
    assert jobs["job_id"].is_unique
    assert set(jobs["experience_group"].dropna()) <= set(du.EXPERIENCE_ORDER)
    assert {du.TECH, du.SOFT} == set(skills["skill_type"].unique())


def test_no_filter_returns_all(data):
    jobs, _, locs = data
    assert len(du.filter_jobs(jobs, locs)) == len(jobs)


def test_category_filter(data):
    jobs, _, locs = data
    out = du.filter_jobs(jobs, locs, categories=["Công nghệ thông tin"])
    assert len(out) == (jobs["category_clean"] == "Công nghệ thông tin").sum()
    assert out["category_clean"].unique().tolist() == ["Công nghệ thông tin"]


def test_location_filter_handles_multi_location(data):
    jobs, _, locs = data
    out = du.filter_jobs(jobs, locs, locations=["Đà Nẵng"])
    assert len(out) > 0
    assert out["location_clean"].str.contains("Đà Nẵng", regex=False).all()
    # tin ghi "Hà Nội | TP. Hồ Chí Minh" phải xuất hiện khi lọc Hà Nội
    multi = jobs["location_clean"].fillna("").str.contains(" | ", regex=False) & \
        jobs["location_clean"].fillna("").str.contains("Hà Nội", regex=False)
    hn = du.filter_jobs(jobs, locs, locations=["Hà Nội"])
    # vài dòng địa điểm còn bẩn (VD: "Hà Nội & Bắc Ninh") nên chấp nhận >= 99%
    assert multi[hn.index].sum() >= 0.99 * multi.sum()


def test_combined_filters_and_keyword(data):
    jobs, _, locs = data
    out = du.filter_jobs(jobs, locs, ["Tài chính - Kế toán - Ngân hàng"], ["Hà Nội"],
                         ["1-2 năm"], keyword="kế toán", salary_only=True)
    assert len(out) > 0
    assert out["salary_for_analysis"].notna().all()
    assert out["job_title"].str.lower().str.contains("kế toán").all()


def test_empty_result_is_handled(data):
    jobs, skills, locs = data
    out = du.filter_jobs(jobs, locs, keyword="zzz-khong-ton-tai-zzz")
    assert out.empty
    k = du.kpis(out, locs, len(jobs))
    assert k["n"] == 0 and k["salary_n"] == 0
    assert du.top_skills(du.filter_skills(skills, out), out).empty
    assert du.salary_stats(out)["n"] == 0
    t = du.compare_table(out, skills, locs, ["Công nghệ thông tin", "Marketing - Truyền thông"])
    assert (t.loc["Số tin tuyển dụng"] == "0").all()
    mv = du.majors_view(du.load_majors(), out, skills, None)
    assert mv["Số tin"].sum() == 0


def test_kpis_full_data_match_tv2_findings(data):
    jobs, _, locs = data
    k = du.kpis(jobs, locs, len(jobs))
    # F2 trong findings.txt của TV2: trung vị 13.0, IQR 10.5–17.5
    assert round(k["salary_median"], 1) == 13.0
    assert round(k["salary_p25"], 1) == 10.5
    assert round(k["salary_p75"], 1) == 17.5


def test_top_skills_percentages(data):
    jobs, skills, locs = data
    d = du.filter_jobs(jobs, locs, ["Công nghệ thông tin"])
    top = du.top_skills(du.filter_skills(skills, d), d, du.TECH, 5)
    assert len(top) == 5
    assert top["% tin"].between(0, 100).all()
    assert top["Số tin"].is_monotonic_decreasing


def test_salary_by_experience_hides_small_samples(data):
    jobs, _, _ = data
    t = du.salary_by_experience(jobs, ["Ngôn ngữ - Dịch thuật"], min_n=10)
    assert (t.loc[t["Số tin có lương"] < 10, "Lương trung vị"].isna()).all()


def test_majors_table_covers_all_categories(data):
    jobs, skills, _ = data
    majors = du.load_majors()
    assert set(jobs["category_clean"].unique()) <= set(majors["category_clean"])
    view = du.majors_view(majors, jobs, skills)
    assert len(view) == len(set(majors["category_clean"]) | set(jobs["category_clean"]))
    assert view["nganh_hoc_goi_y"].ne("").all()


# ---------------------------------------------------------------------------
# Kiểm thử phần nâng cấp: chỉ tiêu theo nhóm nghề, định dạng số, điểm gợi ý
# ---------------------------------------------------------------------------
def test_vietnamese_number_format():
    assert du.fmt_int(47564) == "47.564"
    assert du.fmt_dec(13.5) == "13,5"
    assert du.fmt_pct(28.4) == "28%"
    assert du.fmt_dec(float("nan")) == "—"


def test_category_stats_consistent(data):
    jobs, _, _ = data
    st_ = du.category_stats(jobs)
    assert st_["n"].sum() == len(jobs)
    assert abs(st_["share"].sum() - 100) < 1e-6
    it = st_.set_index("category_clean").loc["Công nghệ thông tin"]
    assert round(it["median"], 1) == 16.0          # khớp F3 của TV2
    assert it["growth"] > 1                        # lương tăng theo kinh nghiệm


def test_concentration_partitions_jobs(data):
    jobs, _, locs = data
    c = du.concentration(jobs, locs)
    assert c["Số tin"].sum() == len(jobs)          # mỗi tin thuộc đúng một nhóm
    assert abs(c["% tin"].sum() - 100) < 1e-6


def test_salary_ladder_monotone_for_market(data):
    jobs, _, _ = data
    lad = du.salary_ladder(jobs)
    med = lad["median"].tolist()
    assert med[-1] > med[0]


def test_match_scores_sum_of_parts(data):
    jobs, _, _ = data
    nat = du.category_stats(jobs)
    majors = du.load_majors()
    tags = du.interest_tags(majors)
    w = {"interest": 5, "entry_salary": 3, "demand": 3, "entry_pct": 3, "growth": 2}
    sc = du.match_scores(nat, nat, tags, ["Máy tính, công nghệ"], w)
    parts = sc[list(du.CRITERIA)].sum(axis=1)
    assert ((parts - sc["score"]).abs() < 1e-9).all()
    assert sc["score"].between(0, 100).all()
    assert du.OTHER_CATEGORY not in set(sc["category_clean"])
    # chọn sở thích công nghệ thì CNTT phải nằm trong top 3
    assert "Công nghệ thông tin" in sc.head(3)["category_clean"].tolist()


def test_match_scores_without_weights_does_not_crash(data):
    jobs, _, _ = data
    nat = du.category_stats(jobs)
    sc = du.match_scores(nat, nat.iloc[0:0], {}, [], {})
    assert len(sc) == len(nat) - 1


def test_every_category_has_interest_tags():
    tags = du.interest_tags(du.load_majors())
    missing = [c for c, t in tags.items() if not t and c != du.OTHER_CATEGORY]
    assert not missing
