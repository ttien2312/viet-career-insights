"""Thành phần giao diện dùng chung: CSS, thẻ chỉ số, chú thích biểu đồ, trạng thái rỗng."""

from __future__ import annotations

import html

import pandas as pd
import streamlit as st

import data_utils as du

SOURCE = "Nguồn: VietJobs, dữ liệu đã làm sạch (nhóm 15)"
PLOTLY_CONFIG = {"displaylogo": False, "displayModeBar": "hover",
                 "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
                 "toImageButtonOptions": {"format": "png", "scale": 2}}

CSS = """
<style>
:root { --ink:#0b0b0b; --ink2:#52514e; --muted:#898781; --line:rgba(11,11,11,.10);
        --blue:#2a78d6; --blue-soft:#eef5fd; --good:#006300; --bad:#b42323; }
.block-container { padding-top: 2.2rem; max-width: 1320px; }
h1, h2, h3 { letter-spacing: -0.01em; }
.vci-hero { padding: 4px 0 6px; }
.vci-hero .eyebrow { color: var(--blue); font-weight: 600; font-size: .85rem; text-transform: uppercase; letter-spacing: .06em; }
.vci-hero h1 { font-size: 2.1rem; margin: .1rem 0 .2rem; color: var(--ink); }
.vci-hero p { color: var(--ink2); font-size: 1.02rem; margin: 0; max-width: 860px; }
.vci-kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; margin: 14px 0 8px; }
.vci-kpi { border: 1px solid var(--line); border-radius: 12px; padding: 14px 16px; background: #fff; }
.vci-kpi .label { color: var(--ink2); font-size: .82rem; line-height: 1.25; min-height: 2.1em; }
.vci-kpi .value { color: var(--ink); font-size: 1.75rem; font-weight: 650; line-height: 1.15; margin-top: 4px; }
.vci-kpi .value small { font-size: .95rem; font-weight: 500; color: var(--ink2); margin-left: 2px; }
.vci-kpi .sub { color: var(--muted); font-size: .8rem; margin-top: 4px; }
.vci-kpi .up { color: var(--good); font-weight: 600; }
.vci-kpi .down { color: var(--bad); font-weight: 600; }
.vci-insight { border-left: 3px solid var(--blue); background: var(--blue-soft); border-radius: 0 10px 10px 0;
               padding: 12px 16px; margin: 6px 0 10px; color: var(--ink); }
.vci-insight ul { margin: 0; padding-left: 1.1rem; }
.vci-insight li { margin: 3px 0; }
.vci-chips { display: flex; flex-wrap: wrap; gap: 6px; margin: 2px 0 8px; align-items: center; }
.vci-chip { border: 1px solid var(--line); border-radius: 999px; padding: 2px 10px; font-size: .8rem; color: var(--ink2); background: #fff; }
.vci-chip.on { border-color: var(--blue); color: var(--blue); background: var(--blue-soft); }
.vci-tags { display: flex; flex-wrap: wrap; gap: 6px; margin: 4px 0 8px; }
.vci-tag { background: #f3f2ee; border-radius: 8px; padding: 3px 9px; font-size: .86rem; color: var(--ink); }
.vci-section { margin-top: 1.4rem; }
.vci-section h3 { margin-bottom: .1rem; }
.vci-section p.lead { color: var(--ink2); margin: 0 0 .4rem; }
.vci-steps { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 10px; margin: 10px 0 4px; }
.vci-step { border: 1px dashed var(--line); border-radius: 12px; padding: 10px 14px; color: var(--ink2); font-size: .9rem; }
.vci-step b { color: var(--ink); }
.vci-rank { font-size: 2rem; font-weight: 700; color: var(--blue); line-height: 1; }
div[data-testid="stCaptionContainer"] p { color: var(--muted); }
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def hero(eyebrow: str, title: str, text: str) -> None:
    st.markdown(f"<div class='vci-hero'><div class='eyebrow'>{eyebrow}</div><h1>{title}</h1>"
                f"<p>{text}</p></div>", unsafe_allow_html=True)


def section(title: str, lead: str = "") -> None:
    lead_html = f"<p class='lead'>{lead}</p>" if lead else ""
    st.markdown(f"<div class='vci-section'><h3>{title}</h3>{lead_html}</div>", unsafe_allow_html=True)


def kpis(items: list[dict]) -> None:
    """items: {label, value, unit?, sub?, delta?, good_when_up?}"""
    cards = []
    for it in items:
        unit = f"<small>{it['unit']}</small>" if it.get("unit") else ""
        sub = it.get("sub", "")
        delta = it.get("delta")
        if delta is not None and not pd.isna(delta) and abs(delta) >= 0.05:
            up = delta > 0
            good = up if it.get("good_when_up", True) else not up
            arrow = "▲" if up else "▼"
            dtxt = it.get("delta_text") or du.fmt_dec(abs(delta))
            sub = f"<span class='{'up' if good else 'down'}'>{arrow} {dtxt}</span> {sub}"
        cards.append(f"<div class='vci-kpi'><div class='label'>{it['label']}</div>"
                     f"<div class='value'>{it['value']}{unit}</div><div class='sub'>{sub}</div></div>")
    st.markdown(f"<div class='vci-kpis'>{''.join(cards)}</div>", unsafe_allow_html=True)


def insight(lines: list[str]) -> None:
    if not lines:
        return
    # chuyển **đậm** của markdown sang thẻ <b>
    items = []
    for line in lines:
        parts = html.escape(line).split("**")
        items.append("".join(f"<b>{p}</b>" if i % 2 else p for i, p in enumerate(parts)))
    st.markdown("<div class='vci-insight'><ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul></div>",
                unsafe_allow_html=True)


def tags(values: list[str]) -> None:
    vals = [v for v in values if v]
    if vals:
        st.markdown("<div class='vci-tags'>" + "".join(f"<span class='vci-tag'>{html.escape(v)}</span>" for v in vals)
                    + "</div>", unsafe_allow_html=True)


def filter_chips(f: dict, applies: str = "all") -> None:
    """Dòng nhắc bộ lọc đang áp dụng ở đầu mỗi trang."""
    chips = []
    if applies == "all" and f["cat"]:
        chips.append(("Nhóm nghề: " + ", ".join(du.short(c) for c in f["cat"]), True))
    if f["loc"]:
        chips.append(("Địa điểm: " + ", ".join(f["loc"]), True))
    if f["exp"]:
        chips.append(("Kinh nghiệm: " + ", ".join(f["exp"]), True))
    if f["kw"]:
        chips.append((f"Từ khóa: “{f['kw']}”", True))
    if f["salary_only"]:
        chips.append(("Chỉ tin có lương", True))
    if not chips:
        chips = [("Toàn bộ dữ liệu – chưa lọc", False)]
    body = "".join(f"<span class='vci-chip {'on' if on else ''}'>{html.escape(t)}</span>" for t, on in chips)
    st.markdown(f"<div class='vci-chips'>{body}</div>", unsafe_allow_html=True)


def note(n: int, unit: str, extra: str = "") -> None:
    text = f"{SOURCE} · Đơn vị: {unit} · Số mẫu: n = {du.fmt_int(n)} tin."
    if extra:
        text += f" {extra}"
    st.caption(text)


def chart(build, *args, key: str, n: int, unit: str, extra: str = "", table: pd.DataFrame | None = None,
          select: bool = False, **kwargs):
    """Vẽ biểu đồ + chú thích nguồn/đơn vị/số mẫu + bảng số liệu tương ứng (tuỳ chọn).

    Lỗi ở một biểu đồ chỉ hiện cảnh báo, không làm dừng trang.
    Trả về sự kiện chọn điểm (nếu select=True) để trang xử lý bấm vào biểu đồ.
    """
    try:
        fig = build(*args, **kwargs)
    except Exception as exc:  # pragma: no cover
        st.warning(f"Không vẽ được biểu đồ này với bộ lọc hiện tại ({type(exc).__name__}).")
        return None
    event = None
    if select:
        event = st.plotly_chart(fig, key=key, theme=None, config=PLOTLY_CONFIG,
                                on_select="rerun", selection_mode="points")
    else:
        st.plotly_chart(fig, key=key, theme=None, config=PLOTLY_CONFIG)
    note(n, unit, extra)
    if table is not None and not table.empty:
        with st.expander("Xem bảng số liệu của biểu đồ"):
            st.dataframe(table, hide_index=True, key=f"{key}_tbl")
    return event


def empty_state(where: str = "") -> None:
    st.warning("Không có tin tuyển dụng nào khớp với bộ lọc hiện tại" + (f" {where}" if where else "") + ".")
    st.markdown("Thử bỏ bớt địa điểm, chọn thêm mức kinh nghiệm, xóa từ khóa, hoặc bấm "
                "**Xóa bộ lọc** ở thanh bên trái.")
