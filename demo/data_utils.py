"""
Các hàm xử lý dữ liệu cho demo Streamlit (TV3).

Tách riêng khỏi app.py để:
- kiểm thử được bằng pytest mà không cần chạy giao diện;
- app.py chỉ lo phần hiển thị.

Dữ liệu đầu vào là đầu ra đã chốt của TV1 trong thư mục data_preprocessing/data.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
JOBS_PATH = ROOT / "data_preprocessing" / "data" / "jobs_clean.csv.gz"
SKILLS_PATH = ROOT / "data_preprocessing" / "data" / "skills_table.csv"
QUALITY_PATH = ROOT / "data_preprocessing" / "data" / "quality_comparison.csv"
MAJORS_PATH = Path(__file__).resolve().parent / "data" / "nganh_hoc_lien_quan.csv"

EXPERIENCE_ORDER = ["Không yêu cầu", "Dưới 1 năm", "1-2 năm", "3-4 năm", "Từ 5 năm"]
TECH = "Kỹ năng chuyên môn"
SOFT = "Kỹ năng mềm"
LOC_SEP = " | "
# Gộp vài cách ghi còn sót sau bước làm sạch của TV1
LOCATION_ALIASES = {"Hồ Chí Minh": "TP. Hồ Chí Minh", "Tp Hcm": "TP. Hồ Chí Minh", "Tp. Hồ Chí Minh": "TP. Hồ Chí Minh"}

JOB_COLUMNS = [
    "job_id",
    "job_title",
    "category_clean",
    "location_clean",
    "experience_group",
    "experience_months",
    "salary_status",
    "salary_for_analysis",
    "contract_type",
    "qualifications",
    "languages_required",
]


# ----------------------------------------------------------------------------
# Nạp dữ liệu
# ----------------------------------------------------------------------------
def load_jobs(path: Path = JOBS_PATH) -> pd.DataFrame:
    """Đọc bảng tin tuyển dụng đã làm sạch, chỉ lấy các cột demo cần."""
    df = pd.read_csv(path, usecols=JOB_COLUMNS)
    for col in ["job_title", "category_clean", "location_clean", "experience_group",
                "salary_status", "contract_type", "qualifications", "languages_required"]:
        df[col] = df[col].astype(object)
    df["job_title"] = df["job_title"].fillna("").astype(str)
    df["category_clean"] = df["category_clean"].fillna("Nhóm nghề khác")
    df["salary_for_analysis"] = pd.to_numeric(df["salary_for_analysis"], errors="coerce")

    # Cờ trình độ được nhắc tới trong yêu cầu (một tin có thể nhắc nhiều mức)
    q = df["qualifications"].fillna("").astype(str).str.lower()
    df["mentions_university"] = q.str.contains(r"đại học|\bđh\b", regex=True)
    df["mentions_college"] = q.str.contains(r"cao đẳng|\bcđ\b", regex=True)
    df["mentions_vocational"] = q.str.contains(r"trung cấp", regex=True)
    return df.reset_index(drop=True)


def load_skills(path: Path = SKILLS_PATH) -> pd.DataFrame:
    """Đọc bảng kỹ năng dạng dài (mỗi dòng = một kỹ năng của một tin)."""
    df = pd.read_csv(path, usecols=["job_id", "category_clean", "skill", "skill_type"])
    for col in df.columns:
        df[col] = df[col].astype(object)
    return df.dropna(subset=["skill"])


def load_quality(path: Path = QUALITY_PATH) -> pd.DataFrame:
    return pd.read_csv(path)


def load_majors(path: Path = MAJORS_PATH) -> pd.DataFrame:
    """Bảng liên hệ nhóm nghề – ngành học (TV4 có thể thay tệp CSV này)."""
    if not Path(path).exists():
        return pd.DataFrame(columns=["category_clean", "nganh_hoc_goi_y"])
    df = pd.read_csv(path).fillna("")
    if "category_clean" not in df.columns and len(df.columns):
        # Cho phép TV4 dùng tên cột khác: cột đầu tiên luôn là nhóm nghề
        df = df.rename(columns={df.columns[0]: "category_clean"})
    return df


def explode_locations(jobs: pd.DataFrame) -> pd.Series:
    """Series (index = chỉ số dòng của jobs) chứa từng địa điểm của mỗi tin.

    Một tin có thể ghi nhiều địa điểm, nối bằng ' | '.
    """
    s = jobs["location_clean"].dropna().astype(str).str.split(LOC_SEP, regex=False).explode()
    # Một số ít dòng còn dạng danh sách Python (VD: "['Hà Nội' | 'Hải Phòng']") -> bỏ ngoặc, nháy
    s = s.str.strip().str.strip("[]'\" ").str.strip()
    s = s.replace(LOCATION_ALIASES)
    return s[s != ""]


def location_options(loc_exploded: pd.Series, min_count: int = 1) -> list[str]:
    """Danh sách địa điểm sắp theo số tin giảm dần."""
    vc = loc_exploded.value_counts()
    return vc[vc >= min_count].index.tolist()


# ----------------------------------------------------------------------------
# Lọc
# ----------------------------------------------------------------------------
def filter_jobs(
    jobs: pd.DataFrame,
    loc_exploded: pd.Series,
    categories: list[str] | None = None,
    locations: list[str] | None = None,
    experiences: list[str] | None = None,
    keyword: str = "",
    salary_only: bool = False,
) -> pd.DataFrame:
    """Lọc tin tuyển dụng. Danh sách rỗng/None nghĩa là không lọc theo tiêu chí đó.

    Kết quả có thể rỗng — app.py có trách nhiệm hiển thị thông báo phù hợp.
    """
    mask = pd.Series(True, index=jobs.index)
    if categories:
        mask &= jobs["category_clean"].isin(categories)
    if experiences:
        mask &= jobs["experience_group"].isin(experiences)
    if locations:
        hit = loc_exploded[loc_exploded.isin(locations)].index.unique()
        mask &= jobs.index.isin(hit)
    kw = (keyword or "").strip()
    if kw:
        mask &= jobs["job_title"].str.contains(kw, case=False, regex=False, na=False)
    if salary_only:
        mask &= jobs["salary_for_analysis"].notna()
    return jobs[mask]


def filter_skills(skills: pd.DataFrame, jobs_subset: pd.DataFrame) -> pd.DataFrame:
    """Giữ các dòng kỹ năng thuộc những tin còn lại sau khi lọc."""
    if jobs_subset.empty:
        return skills.iloc[0:0]
    return skills[skills["job_id"].isin(jobs_subset["job_id"])]


# ----------------------------------------------------------------------------
# Chỉ tiêu
# ----------------------------------------------------------------------------
def salary_stats(df: pd.DataFrame) -> dict:
    s = df["salary_for_analysis"].dropna()
    if s.empty:
        return {"n": 0, "median": np.nan, "p25": np.nan, "p75": np.nan}
    return {
        "n": int(s.size),
        "median": float(s.median()),
        "p25": float(s.quantile(0.25)),
        "p75": float(s.quantile(0.75)),
    }


def kpis(df: pd.DataFrame, loc_exploded: pd.Series, total_rows: int) -> dict:
    """Các chỉ số tóm tắt cho phần Tổng quan."""
    n = len(df)
    sal = salary_stats(df)
    locs = loc_exploded[loc_exploded.index.isin(df.index)]
    negotiable = (df["salary_status"] == "Thỏa thuận").sum() if n else 0
    return {
        "n": n,
        "share_total": n / total_rows * 100 if total_rows else 0.0,
        "salary_n": sal["n"],
        "salary_median": sal["median"],
        "salary_p25": sal["p25"],
        "salary_p75": sal["p75"],
        "negotiable_pct": negotiable / n * 100 if n else np.nan,
        "n_locations": int(locs.nunique()),
        "no_exp_pct": (df["experience_group"] == "Không yêu cầu").mean() * 100 if n else np.nan,
    }


def top_skills(skills_subset: pd.DataFrame, jobs_subset: pd.DataFrame,
               skill_type: str = TECH, n: int = 10) -> pd.DataFrame:
    """Kỹ năng xuất hiện nhiều nhất, kèm % số tin có nhắc tới."""
    cols = ["Kỹ năng", "Số tin", "% tin"]
    if skills_subset.empty or jobs_subset.empty:
        return pd.DataFrame(columns=cols)
    s = skills_subset[skills_subset["skill_type"] == skill_type]
    if s.empty:
        return pd.DataFrame(columns=cols)
    counts = s.drop_duplicates(["job_id", "skill"])["skill"].value_counts().head(n)
    out = counts.rename_axis("Kỹ năng").reset_index(name="Số tin")
    out["% tin"] = out["Số tin"] / len(jobs_subset) * 100
    return out


def top_locations_share(df: pd.DataFrame, loc_exploded: pd.Series, n: int = 3) -> str:
    if df.empty:
        return "—"
    locs = loc_exploded[loc_exploded.index.isin(df.index)]
    vc = locs.value_counts().head(n)
    return ", ".join(f"{k} ({v / len(df) * 100:.0f}%)" for k, v in vc.items())


def top_languages(df: pd.DataFrame, n: int = 2) -> str:
    """Ngoại ngữ được yêu cầu nhiều nhất (bỏ 'tiếng việt' và giá trị thiếu)."""
    if df.empty:
        return "—"
    s = (df["languages_required"].dropna().astype(str).str.lower()
         .str.split(",").explode().str.strip())
    s = s[~s.isin(["", "unk", "tiếng việt", "nan"])]
    if s.empty:
        return "Ít tin yêu cầu"
    vc = s.value_counts().head(n)
    return ", ".join(f"{k.title()} ({v / len(df) * 100:.0f}%)" for k, v in vc.items())


def compare_table(jobs_base: pd.DataFrame, skills: pd.DataFrame, loc_exploded: pd.Series,
                  categories: list[str]) -> pd.DataFrame:
    """Bảng so sánh các nhóm nghề (mỗi cột là một nhóm nghề)."""
    data = {}
    for cat in categories:
        d = jobs_base[jobs_base["category_clean"] == cat]
        sal = salary_stats(d)
        sk = top_skills(filter_skills(skills, d), d, TECH, 3)
        n = len(d)
        data[cat] = {
            "Số tin tuyển dụng": f"{n:,}",
            "Lương trung vị (triệu/tháng)": "—" if sal["n"] == 0 else f"{sal['median']:.1f}",
            "Khoảng lương phổ biến P25–P75": "—" if sal["n"] == 0 else f"{sal['p25']:.1f} – {sal['p75']:.1f}",
            "Số tin có lương công khai": f"{sal['n']:,}",
            "% tin không yêu cầu kinh nghiệm": "—" if n == 0 else
                f"{(d['experience_group'] == 'Không yêu cầu').mean() * 100:.0f}%",
            "% tin nhắc tới trình độ Đại học": "—" if n == 0 else f"{d['mentions_university'].mean() * 100:.0f}%",
            "Địa điểm tuyển nhiều nhất": top_locations_share(d, loc_exploded, 2),
            "Ngoại ngữ hay yêu cầu": top_languages(d),
            "Kỹ năng chuyên môn nổi bật": "—" if sk.empty else ", ".join(sk["Kỹ năng"]),
        }
    return pd.DataFrame(data)


def salary_by_experience(jobs_base: pd.DataFrame, categories: list[str],
                         min_n: int = 10) -> pd.DataFrame:
    """Lương trung vị theo nhóm kinh nghiệm cho từng nhóm nghề.

    Ô có ít hơn min_n tin có lương được để trống (NaN) để tránh kết luận từ mẫu quá nhỏ.
    """
    d = jobs_base[jobs_base["category_clean"].isin(categories)].dropna(subset=["salary_for_analysis"])
    rows = []
    for cat in categories:
        for exp in EXPERIENCE_ORDER:
            s = d[(d["category_clean"] == cat) & (d["experience_group"] == exp)]["salary_for_analysis"]
            rows.append({
                "Nhóm nghề": cat,
                "Kinh nghiệm": exp,
                "Lương trung vị": float(s.median()) if len(s) >= min_n else np.nan,
                "Số tin có lương": int(len(s)),
            })
    return pd.DataFrame(rows)


def experience_distribution(jobs_base: pd.DataFrame, categories: list[str]) -> pd.DataFrame:
    """% tin theo nhóm kinh nghiệm trong từng nhóm nghề."""
    rows = []
    for cat in categories:
        d = jobs_base[jobs_base["category_clean"] == cat]
        n = len(d)
        vc = d["experience_group"].value_counts()
        for exp in EXPERIENCE_ORDER:
            c = int(vc.get(exp, 0))
            rows.append({"Nhóm nghề": cat, "Kinh nghiệm": exp, "Số tin": c,
                         "% tin": c / n * 100 if n else 0.0})
    return pd.DataFrame(rows)


def majors_view(majors: pd.DataFrame, jobs_base: pd.DataFrame, skills: pd.DataFrame,
                categories: list[str] | None = None) -> pd.DataFrame:
    """Ghép bảng ngành học (tĩnh) với số liệu thị trường (tính từ dữ liệu đã lọc)."""
    cats = categories or sorted(set(majors.get("category_clean", pd.Series(dtype=object)))
                                | set(jobs_base["category_clean"].dropna()))
    rows = []
    for cat in cats:
        d = jobs_base[jobs_base["category_clean"] == cat]
        sal = salary_stats(d)
        sk = top_skills(filter_skills(skills, d), d, TECH, 5)
        rows.append({
            "category_clean": cat,
            "Số tin": len(d),
            "Lương trung vị (triệu)": round(sal["median"], 1) if sal["n"] else np.nan,
            "% tin nhắc Đại học": round(d["mentions_university"].mean() * 100) if len(d) else np.nan,
            "% tin nhắc Cao đẳng/Trung cấp": round((d["mentions_college"] | d["mentions_vocational"]).mean() * 100)
            if len(d) else np.nan,
            "Kỹ năng chuyên môn nên chuẩn bị": ", ".join(sk["Kỹ năng"]) if not sk.empty else "",
        })
    market = pd.DataFrame(rows, columns=[
        "category_clean", "Số tin", "Lương trung vị (triệu)", "% tin nhắc Đại học",
        "% tin nhắc Cao đẳng/Trung cấp", "Kỹ năng chuyên môn nên chuẩn bị"])
    out = majors.merge(market, on="category_clean", how="right")
    out = out.rename(columns={"category_clean": "Nhóm nghề"})
    return out


def jobs_table(df: pd.DataFrame) -> pd.DataFrame:
    """Bảng tra cứu tin tuyển dụng (cột tiếng Việt, để hiển thị và tải về)."""
    out = df[["job_id", "job_title", "category_clean", "location_clean", "experience_group",
              "salary_for_analysis", "salary_status", "contract_type"]].copy()
    out.columns = ["Mã tin", "Vị trí", "Nhóm nghề", "Địa điểm", "Kinh nghiệm",
                   "Lương (triệu/tháng)", "Trạng thái lương", "Hợp đồng"]
    return out


# ============================================================================
# Bổ sung cho bản demo nâng cấp (đa trang)
# ============================================================================
ENTRY_LEVELS = ["Không yêu cầu", "Dưới 1 năm"]
SENIOR_LEVELS = ["3-4 năm", "Từ 5 năm"]
OTHER_CATEGORY = "Nhóm nghề khác"
MIN_SALARY_N = 10  # ô có ít hơn số tin có lương này thì không tính trung vị

# Tên ngắn để ghi nhãn trực tiếp trên biểu đồ
SHORT_NAMES = {
    "Kinh doanh - Bán hàng - CSKH": "Kinh doanh – Bán hàng",
    "Sản xuất - Cơ khí - Lao động phổ thông": "Sản xuất – Cơ khí",
    "Marketing - Truyền thông": "Marketing",
    "Tài chính - Kế toán - Ngân hàng": "Tài chính – Kế toán",
    "Du lịch - Nhà hàng - Khách sạn": "Du lịch – Khách sạn",
    "Thiết kế - Nghệ thuật - Truyền thông": "Thiết kế – Nghệ thuật",
    "Nhân sự - Hành chính - Pháp chế": "Nhân sự – Pháp chế",
    "Xây dựng - Kiến trúc - Bất động sản": "Xây dựng – Kiến trúc",
    "Công nghệ thông tin": "CNTT",
    "Logistics - Vận tải - Chuỗi cung ứng": "Logistics",
    "Điện - Điện tử - Viễn thông": "Điện – Điện tử",
    "Giáo dục - Đào tạo - Nghiên cứu": "Giáo dục",
    "Y tế - Dược - Công nghệ sinh học": "Y tế – Dược",
    "Ngôn ngữ - Dịch thuật": "Ngôn ngữ",
    "Nhóm nghề khác": "Khác",
    "Nông nghiệp - Năng lượng - Môi trường": "Nông nghiệp – Môi trường",
}


def short(cat: str) -> str:
    return SHORT_NAMES.get(cat, cat)


# ----------------------------------------------------------------------------
# Định dạng số kiểu Việt Nam: 47.564 ; 13,5 ; 28%
# ----------------------------------------------------------------------------
def _swap(s: str) -> str:
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def fmt_int(v) -> str:
    return "—" if v is None or pd.isna(v) else _swap(f"{int(round(v)):,}")


def fmt_dec(v, digits: int = 1, suffix: str = "") -> str:
    return "—" if v is None or pd.isna(v) else _swap(f"{v:,.{digits}f}") + suffix


def fmt_pct(v, digits: int = 0) -> str:
    return "—" if v is None or pd.isna(v) else _swap(f"{v:.{digits}f}") + "%"


# ----------------------------------------------------------------------------
# Chỉ tiêu theo nhóm nghề
# ----------------------------------------------------------------------------
def _median_or_nan(s: pd.Series, min_n: int = MIN_SALARY_N) -> float:
    s = s.dropna()
    return float(s.median()) if len(s) >= min_n else np.nan


def summary(df: pd.DataFrame) -> dict:
    """Bộ chỉ tiêu dùng chung cho một tập tin tuyển dụng bất kỳ."""
    n = len(df)
    sal = df["salary_for_analysis"]
    entry = df[df["experience_group"].isin(ENTRY_LEVELS)]
    senior = df[df["experience_group"].isin(SENIOR_LEVELS)]
    entry_sal = _median_or_nan(entry["salary_for_analysis"])
    senior_sal = _median_or_nan(senior["salary_for_analysis"])
    s = sal.dropna()
    return {
        "n": n,
        "salary_n": int(s.size),
        "median": float(s.median()) if s.size >= MIN_SALARY_N else np.nan,
        "p25": float(s.quantile(0.25)) if s.size >= MIN_SALARY_N else np.nan,
        "p75": float(s.quantile(0.75)) if s.size >= MIN_SALARY_N else np.nan,
        "entry_pct": len(entry) / n * 100 if n else np.nan,
        "entry_salary": entry_sal,
        "entry_salary_n": int(entry["salary_for_analysis"].notna().sum()),
        "senior_salary": senior_sal,
        "growth": senior_sal / entry_sal if entry_sal and not np.isnan(entry_sal) and not np.isnan(senior_sal) else np.nan,
        "negotiable_pct": (df["salary_status"] == "Thỏa thuận").mean() * 100 if n else np.nan,
        "univ_pct": df["mentions_university"].mean() * 100 if n else np.nan,
        "college_pct": (df["mentions_college"] | df["mentions_vocational"]).mean() * 100 if n else np.nan,
    }


def category_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Một dòng cho mỗi nhóm nghề có trong df, sắp theo số tin giảm dần."""
    cols = ["category_clean", "short", "n", "share", "salary_n", "median", "p25", "p75",
            "entry_pct", "entry_salary", "entry_salary_n", "senior_salary", "growth",
            "negotiable_pct", "univ_pct", "college_pct"]
    if df.empty:
        return pd.DataFrame(columns=cols)
    rows = []
    total = len(df)
    for cat, d in df.groupby("category_clean"):
        r = summary(d)
        r.update({"category_clean": cat, "short": short(cat), "share": len(d) / total * 100})
        rows.append(r)
    return pd.DataFrame(rows)[cols].sort_values("n", ascending=False).reset_index(drop=True)


def salary_ladder(df: pd.DataFrame, min_n: int = MIN_SALARY_N) -> pd.DataFrame:
    """Phân vị lương theo từng mức kinh nghiệm (P25, trung vị, P75)."""
    rows = []
    for exp in EXPERIENCE_ORDER:
        s = df.loc[df["experience_group"] == exp, "salary_for_analysis"].dropna()
        ok = len(s) >= min_n
        rows.append({
            "Kinh nghiệm": exp, "n": int(len(s)),
            "p25": float(s.quantile(.25)) if ok else np.nan,
            "median": float(s.median()) if ok else np.nan,
            "p75": float(s.quantile(.75)) if ok else np.nan,
        })
    return pd.DataFrame(rows)


def location_counts(df: pd.DataFrame, loc_exploded: pd.Series, top: int = 10) -> pd.DataFrame:
    """Số tin theo địa điểm (một tin ghi nhiều nơi được đếm ở mỗi nơi)."""
    if df.empty:
        return pd.DataFrame(columns=["Địa điểm", "Số tin", "% tin"])
    locs = loc_exploded[loc_exploded.index.isin(df.index)]
    vc = locs.value_counts().head(top)
    out = vc.rename_axis("Địa điểm").reset_index(name="Số tin")
    out["% tin"] = out["Số tin"] / len(df) * 100
    return out


def concentration(df: pd.DataFrame, loc_exploded: pd.Series) -> pd.DataFrame:
    """Tỷ trọng tin ở Hà Nội, TP. HCM và nơi khác (mỗi tin chỉ thuộc một nhóm).

    Tin ghi cả hai thành phố được xếp vào nhóm "Cả Hà Nội và TP. HCM".
    """
    if df.empty:
        return pd.DataFrame(columns=["Nhóm", "Số tin", "% tin"])
    locs = loc_exploded[loc_exploded.index.isin(df.index)]
    hn = set(locs[locs == "Hà Nội"].index)
    hcm = set(locs[locs == "TP. Hồ Chí Minh"].index)
    both = hn & hcm
    groups = {
        "Hà Nội": len(hn - both),
        "TP. Hồ Chí Minh": len(hcm - both),
        "Cả hai thành phố": len(both),
        "Tỉnh, thành khác": len(df) - len(hn | hcm),
    }
    out = pd.DataFrame({"Nhóm": list(groups), "Số tin": list(groups.values())})
    out["% tin"] = out["Số tin"] / len(df) * 100
    return out


def title_examples(df: pd.DataFrame, n: int = 8) -> pd.DataFrame:
    """Các vị trí hay gặp (chuẩn hóa chữ hoa), kèm số tin và lương trung vị."""
    if df.empty:
        return pd.DataFrame(columns=["Vị trí", "Số tin", "Lương trung vị (triệu)"])
    d = df.assign(_t=df["job_title"].str.strip().str.title())
    g = d.groupby("_t")
    out = pd.DataFrame({"Số tin": g.size(),
                        "Lương trung vị (triệu)": g["salary_for_analysis"].median()})
    out = out.sort_values("Số tin", ascending=False).head(n).rename_axis("Vị trí").reset_index()
    return out


def languages_table(df: pd.DataFrame, n: int = 4) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["Ngoại ngữ", "% tin"])
    s = (df["languages_required"].dropna().astype(str).str.lower()
         .str.split(",").explode().str.strip())
    s = s[~s.isin(["", "unk", "tiếng việt", "nan"])]
    vc = s.value_counts().head(n)
    return pd.DataFrame({"Ngoại ngữ": [k.title() for k in vc.index], "% tin": vc.values / len(df) * 100})


# ----------------------------------------------------------------------------
# Nhận xét tự động (câu ngắn có số liệu)
# ----------------------------------------------------------------------------
def market_insights(stats: pd.DataFrame, overall: dict, conc: pd.DataFrame) -> list[str]:
    st_ = stats[stats["category_clean"] != OTHER_CATEGORY]
    out = []
    if len(st_) >= 3:
        top3 = st_.head(3)
        out.append(f"3 nhóm nghề tuyển nhiều nhất ({', '.join(top3['short'])}) chiếm "
                   f"**{fmt_pct(top3['share'].sum())}** số tin.")
    es = st_.dropna(subset=["entry_salary"])
    if len(es) >= 2:
        best = es.sort_values("entry_salary", ascending=False).iloc[0]
        out.append(f"Lương khởi điểm cao nhất: **{best['short']}** "
                   f"({fmt_dec(best['entry_salary'])} triệu/tháng, toàn thị trường "
                   f"{fmt_dec(overall['entry_salary'])} triệu).")
    if len(st_) >= 2:
        easy = st_.sort_values("entry_pct", ascending=False).iloc[0]
        out.append(f"Dễ vào nghề nhất: **{easy['short']}** – {fmt_pct(easy['entry_pct'])} tin "
                   "nhận người chưa có hoặc dưới 1 năm kinh nghiệm.")
    gr = st_.dropna(subset=["growth"])
    if len(gr) >= 2:
        g = gr.sort_values("growth", ascending=False).iloc[0]
        out.append(f"Lương tăng mạnh nhất theo kinh nghiệm: **{g['short']}** – nhóm 3 năm trở lên "
                   f"có trung vị gấp **{fmt_dec(g['growth'])} lần** người mới.")
    if not conc.empty:
        two = conc.loc[conc["Nhóm"] != "Tỉnh, thành khác", "% tin"].sum()
        out.append(f"**{fmt_pct(two)}** số tin ở Hà Nội hoặc TP. Hồ Chí Minh.")
    return out


def profile_insights(cat: str, row: dict, market: dict, stats: pd.DataFrame) -> list[str]:
    out = []
    ranked = stats[stats["category_clean"] != OTHER_CATEGORY].reset_index(drop=True)
    if cat in set(ranked["category_clean"]):
        rank_n = int(ranked.index[ranked["category_clean"] == cat][0]) + 1
        out.append(f"Đứng **thứ {rank_n}/{len(ranked)}** về số tin tuyển dụng "
                   f"({fmt_pct(row['share'], 1)} toàn thị trường).")
    if not np.isnan(row["median"]) and not np.isnan(market["median"]):
        diff = (row["median"] / market["median"] - 1) * 100
        word = "cao hơn" if diff > 0 else "thấp hơn"
        if abs(diff) < 2:
            out.append(f"Lương trung vị {fmt_dec(row['median'])} triệu – **ngang** mặt bằng chung.")
        else:
            out.append(f"Lương trung vị {fmt_dec(row['median'])} triệu – **{word} {fmt_pct(abs(diff))}** "
                       "so với toàn thị trường.")
    if not np.isnan(row["entry_pct"]):
        out.append(f"**{fmt_pct(row['entry_pct'])}** tin nhận người chưa có hoặc dưới 1 năm kinh nghiệm "
                   f"(toàn thị trường {fmt_pct(market['entry_pct'])}).")
    if not np.isnan(row.get("growth", np.nan)):
        out.append(f"Có từ 3 năm kinh nghiệm, lương trung vị gấp **{fmt_dec(row['growth'])} lần** người mới.")
    return out


# ----------------------------------------------------------------------------
# Gợi ý nhóm nghề theo sở thích và ưu tiên (điểm minh bạch, cộng từng phần)
# ----------------------------------------------------------------------------
CRITERIA = {
    "interest": "Hợp sở thích",
    "entry_salary": "Lương khởi điểm",
    "demand": "Nhiều việc làm",
    "entry_pct": "Dễ vào nghề",
    "growth": "Tăng lương theo kinh nghiệm",
}


def interest_tags(majors: pd.DataFrame) -> dict[str, list[str]]:
    """Nhóm nghề -> danh sách thẻ sở thích (cột 'so_thich', ngăn bằng dấu ;)."""
    if "so_thich" not in majors.columns:
        return {}
    return {r["category_clean"]: [t.strip() for t in str(r["so_thich"]).split(";") if t.strip()]
            for _, r in majors.iterrows()}


def all_tags(majors: pd.DataFrame) -> list[str]:
    seen = []
    for tags in interest_tags(majors).values():
        for t in tags:
            if t not in seen:
                seen.append(t)
    return seen


def _minmax(s: pd.Series) -> pd.Series:
    s = s.astype(float)
    lo, hi = s.min(), s.max()
    if pd.isna(lo) or hi == lo:
        return pd.Series(0.5, index=s.index)
    return ((s - lo) / (hi - lo)).fillna(0.0)


def match_scores(stats_national: pd.DataFrame, stats_local: pd.DataFrame, tags: dict[str, list[str]],
                 chosen_tags: list[str], weights: dict[str, float]) -> pd.DataFrame:
    """Tính điểm phù hợp 0–100 cho từng nhóm nghề.

    - Mỗi tiêu chí được chuẩn hóa min–max về 0–1 giữa các nhóm nghề.
    - Nhu cầu (số tin) dùng thang log để vài nhóm rất lớn không lấn át.
    - Số tin và % dễ vào nghề lấy theo địa điểm đã chọn (stats_local);
      lương và mức tăng lương lấy toàn quốc (stats_national) để đủ mẫu.
    - Điểm = tổng (trọng số × giá trị chuẩn hóa) / tổng trọng số × 100,
      nên mỗi phần đóng góp cộng lại đúng bằng điểm.
    """
    nat = stats_national[stats_national["category_clean"] != OTHER_CATEGORY].set_index("category_clean")
    loc = stats_local.set_index("category_clean") if not stats_local.empty else nat.iloc[0:0]
    cats = nat.index
    demand = loc["n"].reindex(cats).fillna(0)
    entry = loc["entry_pct"].reindex(cats)
    entry = entry.fillna(nat["entry_pct"])
    raw = pd.DataFrame({
        "entry_salary": nat["entry_salary"].fillna(nat["entry_salary"].median()),
        "demand": np.log1p(demand),
        "entry_pct": entry,
        "growth": nat["growth"].fillna(nat["growth"].median()),
    }, index=cats)
    norm = raw.apply(_minmax)
    chosen = set(chosen_tags or [])
    if chosen:
        norm["interest"] = [len(chosen & set(tags.get(c, []))) / len(chosen) for c in cats]
    else:
        norm["interest"] = 0.0
    w = {k: float(weights.get(k, 0)) for k in CRITERIA}
    if not chosen:
        w["interest"] = 0.0
    total_w = sum(w.values()) or 1.0
    contrib = pd.DataFrame({k: norm[k] * w[k] / total_w * 100 for k in CRITERIA}, index=cats)
    out = contrib.copy()
    out["score"] = contrib.sum(axis=1)
    out["n_local"] = demand.astype(int)
    out["short"] = [short(c) for c in cats]
    return out.sort_values("score", ascending=False).rename_axis("category_clean").reset_index()
