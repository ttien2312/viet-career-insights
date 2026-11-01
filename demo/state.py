"""Dữ liệu dùng chung giữa các trang + bộ nhớ đệm (cache) để thao tác mượt.

- Dữ liệu gốc đọc một lần cho cả phiên (cache_resource).
- Kết quả lọc và các bảng tổng hợp được lưu theo bộ lọc (cache_data, khóa = bộ lọc),
  nên quay lại một bộ lọc đã dùng là hiện ngay.
"""

from __future__ import annotations

import streamlit as st

import data_utils as du

FILTER_DEFAULTS = {"f_cat": [], "f_loc": [], "f_exp": [], "f_kw": "", "f_salary": False}
PAGES: dict = {}  # app.py đăng ký các trang ở đây để chuyển trang bằng st.switch_page


@st.cache_resource(show_spinner="Đang tải dữ liệu tuyển dụng (chỉ lần đầu)…")
def load():
    jobs = du.load_jobs()
    skills = du.load_skills()
    locs = du.explode_locations(jobs)
    return jobs, skills, locs


@st.cache_data(show_spinner=False)
def static():
    quality = du.load_quality()
    majors = du.load_majors()
    path = du.ROOT / "data_visualization" / "output" / "findings.txt"
    findings = [x for x in path.read_text(encoding="utf-8").splitlines() if x.strip()] if path.exists() else []
    return quality, majors, findings


# ----------------------------------------------------------------------------
# Bộ lọc
# ----------------------------------------------------------------------------
def init_filters() -> None:
    for k, v in FILTER_DEFAULTS.items():
        st.session_state.setdefault(k, v)


def reset_filters() -> None:
    for k, v in FILTER_DEFAULTS.items():
        st.session_state[k] = v


def current() -> dict:
    s = st.session_state
    return {"cat": tuple(s.get("f_cat", [])), "loc": tuple(s.get("f_loc", [])), "exp": tuple(s.get("f_exp", [])),
            "kw": (s.get("f_kw") or "").strip(), "salary_only": bool(s.get("f_salary", False))}


def _key(f: dict, with_cat: bool = True) -> tuple:
    return (f["cat"] if with_cat else (), f["loc"], f["exp"], f["kw"].lower(), f["salary_only"])


@st.cache_data(max_entries=128, show_spinner=False)
def _index(key: tuple):
    jobs, _, locs = load()
    cat, loc, exp, kw, sal = key
    return du.filter_jobs(jobs, locs, list(cat), list(loc), list(exp), kw, sal).index


def jobs(f: dict | None = None, with_cat: bool = True):
    """Tin tuyển dụng theo bộ lọc. with_cat=False: bỏ qua bộ lọc nhóm nghề."""
    f = f or current()
    all_jobs, _, _ = load()
    return all_jobs.loc[_index(_key(f, with_cat))]


@st.cache_data(max_entries=128, show_spinner=False)
def _stats(key: tuple):
    jobs_, _, _ = load()
    return du.category_stats(jobs_.loc[_index(key)])


@st.cache_data(max_entries=128, show_spinner=False)
def _summary(key: tuple):
    jobs_, _, _ = load()
    return du.summary(jobs_.loc[_index(key)])


def stats(f: dict | None = None, with_cat: bool = True):
    return _stats(_key(f or current(), with_cat))


def summary(f: dict | None = None, with_cat: bool = True) -> dict:
    return _summary(_key(f or current(), with_cat))


NATIONAL = {"cat": (), "loc": (), "exp": (), "kw": "", "salary_only": False}


def national_stats():
    return _stats(_key(NATIONAL))


def national_summary():
    return _summary(_key(NATIONAL))


@st.cache_data(max_entries=512, show_spinner=False)
def _top_skills(key: tuple, cat: str | None, skill_type: str, n: int):
    jobs_, skills, _ = load()
    d = jobs_.loc[_index(key)]
    if cat:
        d = d[d["category_clean"] == cat]
    return du.top_skills(du.filter_skills(skills, d), d, skill_type, n)


def top_skills(f: dict | None = None, cat: str | None = None, skill_type: str = du.TECH, n: int = 10,
               with_cat: bool = True):
    return _top_skills(_key(f or current(), with_cat), cat, skill_type, n)


def go_profile(cat: str) -> None:
    """Mở trang Hồ sơ nghề cho nhóm nghề được chọn."""
    st.session_state["profile_cat"] = cat
    st.session_state["_keep_profile_cat"] = cat
    if "profile" in PAGES:
        st.switch_page(PAGES["profile"])


# ----------------------------------------------------------------------------
# Giữ lựa chọn của người dùng khi chuyển trang
# (Streamlit xoá trạng thái của ô nhập không hiển thị ở trang hiện tại)
# ----------------------------------------------------------------------------
def keep(key: str, default) -> None:
    """Gọi TRƯỚC khi vẽ ô nhập có khóa `key`: khôi phục giá trị đã chọn lần trước."""
    if key not in st.session_state:
        st.session_state[key] = st.session_state.get("_keep_" + key, default)


def remember(key: str) -> None:
    """Gọi SAU khi vẽ ô nhập: lưu giá trị hiện tại để dùng khi quay lại trang."""
    if key in st.session_state:
        st.session_state["_keep_" + key] = st.session_state[key]
