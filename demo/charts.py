"""
Biểu đồ của demo (Plotly).

Một hệ màu và kiểu chữ thống nhất cho mọi biểu đồ:
- Một chuỗi dữ liệu -> một màu (xanh). Muốn làm nổi một mục -> mục đó xanh, còn lại xám.
- So sánh 2–3 nhóm nghề -> 3 màu xanh / cam / xanh ngọc (đã kiểm tra phân biệt được
  với người mù màu), màu đi theo nhóm nghề, không đổi khi thêm/bớt.
- Đại lượng có thứ tự (mức kinh nghiệm, cường độ) -> một tông xanh từ nhạt đến đậm.
- Số kiểu Việt Nam: phẩy thập phân, chấm hàng nghìn.

Các biểu đồ phân tích của TV2 (data_visualization/data_analysis.py) được gọi lại nguyên
hàm, rồi áp cùng hệ màu này để demo nhìn thống nhất.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "data_visualization"))

import data_analysis as tv2  # noqa: E402  (hàm vẽ của TV2)

import data_utils as du  # noqa: E402

# ----------------------------------------------------------------------------
# Hệ màu
# ----------------------------------------------------------------------------
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
GREY = "#c9c7bf"
BLUE = "#2a78d6"
BLUE_LIGHT = "#9ec5f4"
BLUE_DARK = "#104281"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
YELLOW = "#eda100"
MAGENTA = "#e87ba4"
SERIES = [BLUE, ORANGE, AQUA]                       # tối đa 3 nhóm nghề khi so sánh
CRITERIA_COLORS = [BLUE, ORANGE, AQUA, YELLOW, MAGENTA]  # 5 thành phần điểm gợi ý
ORDINAL5 = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#0d366b"]  # 5 mức kinh nghiệm
SEQ_SCALE = [[0, "#f3f8fe"], [0.15, "#cde2fb"], [0.35, "#86b6ef"], [0.6, "#3987e5"],
             [0.8, "#1c5cab"], [1, "#0d366b"]]
FONT = "Inter, 'Segoe UI', system-ui, -apple-system, sans-serif"

pio.templates["vci"] = go.layout.Template(layout=dict(
    font=dict(family=FONT, size=13, color=INK2),
    title=dict(font=dict(size=15, color=INK), x=0, xanchor="left", y=0.98, yanchor="top"),
    separators=",.",
    paper_bgcolor="white",
    plot_bgcolor="white",
    colorway=SERIES,
    margin=dict(l=8, r=24, t=48, b=8),
    hoverlabel=dict(bgcolor="white", bordercolor=GRID, font=dict(family=FONT, size=13, color=INK)),
    xaxis=dict(gridcolor=GRID, linecolor=AXIS, zeroline=False, ticks="", automargin=True,
               title=dict(font=dict(size=12, color=INK2)), tickfont=dict(color=INK2)),
    yaxis=dict(gridcolor=GRID, linecolor=AXIS, zeroline=False, ticks="", automargin=True,
               title=dict(font=dict(size=12, color=INK2)), tickfont=dict(color=INK2)),
    legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0,
                font=dict(size=12, color=INK2), title=dict(text="")),
    bargap=0.28,
))


def finish(fig: go.Figure, height: int | None = None, title: str | None = None) -> go.Figure:
    """Áp kiểu chung (dùng cho cả biểu đồ của TV2)."""
    fig.update_layout(template="vci", plot_bgcolor="white", paper_bgcolor="white")
    if title is not None:
        fig.update_layout(title_text=title)
    if height:
        fig.update_layout(height=height)
    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)
    fig.update_traces(cliponaxis=False, selector=dict(type="bar"))
    fig.update_traces(cliponaxis=False, selector=dict(type="scatter"))
    return fig


def _empty(msg: str = "Không đủ dữ liệu để vẽ") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=msg, showarrow=False, font=dict(color=MUTED, size=14),
                       xref="paper", yref="paper", x=0.5, y=0.5)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return finish(fig, 240)


# ----------------------------------------------------------------------------
# 1. Ma trận cơ hội nghề nghiệp (biểu đồ chủ đạo)
# ----------------------------------------------------------------------------
# Vị trí nhãn để các nhãn không đè nhau (chỉnh tay sau khi xem biểu đồ)
_LABEL_POS = {
    "Kinh doanh – Bán hàng": "top center", "Sản xuất – Cơ khí": "bottom center",
    "Marketing": "bottom center", "Tài chính – Kế toán": "bottom center",
    "Du lịch – Khách sạn": "top center", "Thiết kế – Nghệ thuật": "middle right",
    "Nhân sự – Pháp chế": "bottom center", "Xây dựng – Kiến trúc": "top center",
    "CNTT": "bottom center", "Logistics": "middle left", "Điện – Điện tử": "top center",
    "Giáo dục": "bottom right", "Y tế – Dược": "middle right", "Ngôn ngữ": "top center",
    "Nông nghiệp – Môi trường": "bottom center",
}


def opportunity_matrix(stats: pd.DataFrame, market: dict, highlight: list[str] | None = None) -> go.Figure:
    """Trục x: lương khởi điểm; trục y: % tin cho người mới; cỡ bong bóng: số tin."""
    d = stats[(stats["category_clean"] != du.OTHER_CATEGORY)].dropna(subset=["entry_salary", "entry_pct"])
    if len(d) < 2:
        return _empty("Cần ít nhất 2 nhóm nghề đủ dữ liệu lương để vẽ ma trận")
    hl = set(highlight or [])
    colors = [BLUE if (not hl or c in hl) else GREY for c in d["category_clean"]]
    size_ref = 2.0 * d["n"].max() / (58 ** 2)
    fig = go.Figure(go.Scatter(
        x=d["entry_salary"], y=d["entry_pct"], mode="markers+text",
        text=d["short"], textposition=[_LABEL_POS.get(s, "top center") for s in d["short"]],
        textfont=dict(size=12, color=INK),
        marker=dict(size=d["n"], sizemode="area", sizeref=size_ref, sizemin=7, color=colors,
                    opacity=0.78, line=dict(color="white", width=2)),
        customdata=np.stack([d["category_clean"], d["n"], d["median"], d["growth"], d["entry_salary_n"]], axis=-1),
        hovertemplate=("<b>%{customdata[0]}</b><br>Lương khởi điểm: %{x:.1f} triệu "
                       "(n = %{customdata[4]:,})<br>Tin cho người mới: %{y:.0f}%<br>"
                       "Số tin: %{customdata[1]:,}<br>Lương trung vị chung: %{customdata[2]:.1f} triệu"
                       "<extra></extra>"),
    ))
    mx, my = market.get("entry_salary"), market.get("entry_pct")
    if mx and not np.isnan(mx):
        fig.add_vline(x=mx, line=dict(color=AXIS, width=1))
        fig.add_annotation(x=mx, y=1.0, yref="paper", text=f"Toàn thị trường: {du.fmt_dec(mx)} tr",
                           showarrow=False, yanchor="bottom", font=dict(size=11, color=MUTED))
    if my and not np.isnan(my):
        fig.add_hline(y=my, line=dict(color=AXIS, width=1))
        fig.add_annotation(x=1.0, xref="paper", y=my, text=f"{du.fmt_pct(my)}", showarrow=False,
                           xanchor="left", font=dict(size=11, color=MUTED))
    # Nhãn 4 góc phần tư
    corners = [(1, 1, "right", "top", "Dễ vào nghề · lương khởi điểm cao"),
               (0, 1, "left", "top", "Dễ vào nghề · lương khởi điểm thấp hơn"),
               (1, 0, "right", "bottom", "Cần kinh nghiệm · lương khởi điểm cao"),
               (0, 0, "left", "bottom", "Cần kinh nghiệm · lương khởi điểm thấp hơn")]
    for x, y, xa, ya, t in corners:
        fig.add_annotation(x=x, y=y, xref="paper", yref="paper", text=t, showarrow=False,
                           xanchor=xa, yanchor=ya, font=dict(size=11, color=MUTED))
    pad_x = (d["entry_salary"].max() - d["entry_salary"].min()) * 0.12 + 0.3
    pad_y = (d["entry_pct"].max() - d["entry_pct"].min()) * 0.15 + 2
    fig.update_xaxes(title_text="Lương khởi điểm – trung vị tin cho người mới (triệu VND/tháng)",
                     range=[d["entry_salary"].min() - pad_x, d["entry_salary"].max() + pad_x], showgrid=False)
    fig.update_yaxes(title_text="% tin nhận người chưa có / dưới 1 năm kinh nghiệm",
                     range=[d["entry_pct"].min() - pad_y, d["entry_pct"].max() + pad_y],
                     ticksuffix="%", showgrid=False)
    return finish(fig, 560)


# ----------------------------------------------------------------------------
# 2. Xếp hạng nhóm nghề theo một chỉ tiêu
# ----------------------------------------------------------------------------
RANK_METRICS = {
    "Số tin tuyển dụng": ("n", "{:,.0f}", "số tin"),
    "Lương trung vị": ("median", "{:.1f}", "triệu VND/tháng"),
    "Lương khởi điểm": ("entry_salary", "{:.1f}", "triệu VND/tháng"),
    "Dễ vào nghề": ("entry_pct", "{:.0f}%", "% tin cho người mới"),
    "Tăng lương theo kinh nghiệm": ("growth", "{:.2f}×", "lần (3+ năm so với người mới)"),
}


def ranked_bar(stats: pd.DataFrame, metric: str, highlight: list[str] | None = None) -> go.Figure:
    col, fmt, unit = RANK_METRICS[metric]
    # "Nhóm nghề khác" gom nhiều nghề không cùng loại -> không xếp hạng (giống ma trận cơ hội)
    d = stats[stats["category_clean"] != du.OTHER_CATEGORY].dropna(subset=[col]).sort_values(col)
    if d.empty:
        return _empty()
    hl = set(highlight or [])
    colors = [BLUE if (not hl or c in hl) else GREY for c in d["category_clean"]]
    labels = [du._swap(fmt.format(v)) for v in d[col]]
    fig = go.Figure(go.Bar(
        x=d[col], y=d["short"], orientation="h", marker=dict(color=colors, cornerradius=4),
        text=labels, textposition="outside", textfont=dict(color=INK2, size=12),
        customdata=np.stack([d["category_clean"], d["n"]], axis=-1),
        hovertemplate="<b>%{customdata[0]}</b><br>" + metric + ": %{text}<br>Số tin: %{customdata[1]:,}<extra></extra>",
    ))
    fig.update_xaxes(title_text=unit.capitalize(), showgrid=True, rangemode="tozero")
    fig.update_yaxes(title_text="", showgrid=False)
    return finish(fig, max(320, 30 * len(d) + 80))


# ----------------------------------------------------------------------------
# 3. Địa điểm
# ----------------------------------------------------------------------------
def concentration_bar(conc: pd.DataFrame) -> go.Figure:
    """Thanh phần trăm 100%: Hà Nội / TP.HCM / cả hai / nơi khác."""
    if conc.empty:
        return _empty()
    colors = [BLUE, ORANGE, AQUA, GREY]
    fig = go.Figure()
    for (_, r), c in zip(conc.iterrows(), colors):
        fig.add_trace(go.Bar(
            x=[r["% tin"]], y=[""], orientation="h", name=r["Nhóm"], marker=dict(color=c, line=dict(color="white", width=2)),
            text=[f"{r['Nhóm']}<br><b>{du.fmt_pct(r['% tin'])}</b>" if r["% tin"] >= 9 else ""],
            textposition="inside", insidetextanchor="middle",
            textfont=dict(color="white" if c != GREY else INK, size=12),
            hovertemplate=f"{r['Nhóm']}: %{{x:.1f}}% ({du.fmt_int(r['Số tin'])} tin)<extra></extra>",
        ))
    fig.update_layout(barmode="stack", showlegend=True, bargap=0.1,
                      legend=dict(orientation="h", y=-0.25, yanchor="top", traceorder="normal"))
    fig.update_xaxes(range=[0, 100], visible=False)
    fig.update_yaxes(visible=False)
    fig = finish(fig, 170)
    fig.update_layout(margin=dict(l=4, r=4, t=8, b=8), legend=dict(y=-0.08, yanchor="top"))
    return fig


def location_bar(loc: pd.DataFrame) -> go.Figure:
    if loc.empty:
        return _empty()
    d = loc.sort_values("Số tin")
    fig = go.Figure(go.Bar(
        x=d["Số tin"], y=d["Địa điểm"], orientation="h", marker=dict(color=BLUE, cornerradius=4),
        text=[f"{du.fmt_int(v)}  ·  {du.fmt_pct(p)}" for v, p in zip(d["Số tin"], d["% tin"])],
        textposition="outside", textfont=dict(color=INK2, size=12),
        hovertemplate="%{y}: %{x:,} tin<extra></extra>",
    ))
    fig.update_xaxes(title_text="Số tin tuyển dụng", rangemode="tozero")
    fig.update_yaxes(showgrid=False)
    return finish(fig, max(300, 30 * len(d) + 80))


# ----------------------------------------------------------------------------
# 4. Thang lương theo kinh nghiệm (một nhóm nghề so với toàn thị trường)
# ----------------------------------------------------------------------------
def salary_ladder(ladder: pd.DataFrame, market: pd.DataFrame, name: str) -> go.Figure:
    if ladder["median"].notna().sum() == 0:
        return _empty("Chưa đủ tin có lương ở từng mức kinh nghiệm")
    x = ladder["Kinh nghiệm"]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=x, y=ladder["p75"] - ladder["p25"], base=ladder["p25"], name="Khoảng phổ biến (P25–P75)",
        marker=dict(color=BLUE_LIGHT, cornerradius=4), width=0.42,
        customdata=np.stack([ladder["p25"], ladder["p75"], ladder["n"]], axis=-1),
        hovertemplate="%{x}<br>50% tin ở giữa: %{customdata[0]:.1f}–%{customdata[1]:.1f} triệu"
                      "<br>n = %{customdata[2]:,} tin có lương<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=x, y=ladder["median"], mode="markers+text+lines", name=f"Trung vị – {name}",
        line=dict(color=BLUE_DARK, width=2), marker=dict(size=10, color=BLUE_DARK, line=dict(color="white", width=2)),
        text=[du.fmt_dec(v) for v in ladder["median"]], textposition="top left",
        textfont=dict(color=INK, size=12),
        hovertemplate="%{x}: trung vị %{y:.1f} triệu<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=market["Kinh nghiệm"], y=market["median"], mode="lines+markers", name="Trung vị – toàn thị trường",
        line=dict(color=MUTED, width=2), marker=dict(size=7, color=MUTED, symbol="diamond"),
        hovertemplate="%{x}: toàn thị trường %{y:.1f} triệu<extra></extra>",
    ))
    fig.update_yaxes(title_text="Triệu VND/tháng", rangemode="tozero")
    fig.update_xaxes(title_text="Kinh nghiệm yêu cầu", showgrid=False)
    return finish(fig, 420)


# ----------------------------------------------------------------------------
# 5. Kỹ năng
# ----------------------------------------------------------------------------
def skills_bar(top: pd.DataFrame, color: str = BLUE, title: str | None = None) -> go.Figure:
    if top.empty:
        return _empty("Không có dữ liệu kỹ năng")
    d = top.sort_values("Số tin")
    fig = go.Figure(go.Bar(
        x=d["% tin"], y=d["Kỹ năng"], orientation="h", marker=dict(color=color, cornerradius=4),
        text=[du.fmt_pct(v, 1) for v in d["% tin"]], textposition="outside", textfont=dict(color=INK2, size=12),
        customdata=d["Số tin"],
        hovertemplate="%{y}<br>%{x:.1f}% số tin (%{customdata:,} tin)<extra></extra>",
    ))
    fig.update_xaxes(title_text="% số tin có nhắc tới", ticksuffix="%", rangemode="tozero")
    fig.update_yaxes(showgrid=False)
    return finish(fig, max(300, 28 * len(d) + 90), title)


def skills_dot_matrix(tops: dict[str, pd.DataFrame], colors: dict[str, str]) -> go.Figure:
    """Hàng = kỹ năng, cột = nhóm nghề, cỡ chấm = % tin. Thấy ngay kỹ năng chung và riêng."""
    skills = []
    for t in tops.values():
        for s in t["Kỹ năng"].head(6):
            if s not in skills:
                skills.append(s)
    if not skills:
        return _empty("Không có dữ liệu kỹ năng")
    fig = go.Figure()
    mx = max(float(t["% tin"].max()) for t in tops.values() if not t.empty) or 1
    for cat, t in tops.items():
        m = t.set_index("Kỹ năng")["% tin"].reindex(skills).fillna(0)
        fig.add_trace(go.Scatter(
            x=[du.short(cat)] * len(skills), y=skills, mode="markers+text", name=du.short(cat),
            marker=dict(size=[6 + 34 * (v / mx) ** 0.5 if v > 0 else 0 for v in m], color=colors[cat],
                        opacity=0.85, line=dict(color="white", width=2)),
            text=[du.fmt_pct(v, 0) if v >= 1 else "" for v in m], textposition="middle right",
            textfont=dict(size=11, color=INK2),
            hovertemplate=f"<b>{cat}</b><br>%{{y}}: %{{customdata:.1f}}% số tin<extra></extra>",
            customdata=m.values,
        ))
    fig.update_yaxes(autorange="reversed", showgrid=True)
    fig.update_xaxes(showgrid=False, side="top")
    fig.update_layout(showlegend=False)
    return finish(fig, max(320, 34 * len(skills) + 80))


# ----------------------------------------------------------------------------
# 6. So sánh nhóm nghề
# ----------------------------------------------------------------------------
RADAR_AXES = {
    "Nhu cầu tuyển dụng": "n",
    "Lương trung vị": "median",
    "Lương khởi điểm": "entry_salary",
    "Dễ vào nghề": "entry_pct",
    "Tăng lương theo KN": "growth",
}


def radar(stats: pd.DataFrame, cats: list[str], colors: dict[str, str]) -> go.Figure:
    """Mỗi trục = thứ hạng phần trăm của nhóm nghề trong 15 nhóm (0 = thấp nhất, 100 = cao nhất)."""
    base = stats[stats["category_clean"] != du.OTHER_CATEGORY].set_index("category_clean")
    pct = pd.DataFrame({k: base[v].rank(pct=True) * 100 for k, v in RADAR_AXES.items()})
    axes = list(RADAR_AXES)
    fig = go.Figure()
    for cat in cats:
        if cat not in pct.index:
            continue
        r = pct.loc[cat, axes].fillna(0).tolist()
        raw = [base.loc[cat, RADAR_AXES[a]] for a in axes]
        fig.add_trace(go.Scatterpolar(
            r=r + r[:1], theta=axes + axes[:1], name=du.short(cat), fill="toself",
            line=dict(color=colors[cat], width=2), fillcolor=colors[cat], opacity=0.75,
            customdata=raw + raw[:1],
            hovertemplate="<b>" + cat + "</b><br>%{theta}: hạng %{r:.0f}/100 (giá trị %{customdata:.3g})<extra></extra>",
        ))
        fig.data[-1].update(fillcolor=_alpha(colors[cat], 0.12))
    fig.update_layout(polar=dict(
        bgcolor="rgba(0,0,0,0)",
        radialaxis=dict(range=[0, 100], tickvals=[25, 50, 75, 100], gridcolor=GRID, linecolor=GRID,
                        tickfont=dict(size=10, color=MUTED), angle=90),
        angularaxis=dict(gridcolor=GRID, linecolor=AXIS, tickfont=dict(size=12, color=INK)),
    ))
    fig = finish(fig, 440)
    fig.update_layout(margin=dict(l=110, r=110, t=60, b=40), legend=dict(y=1.12))
    return fig


def _alpha(hex_color: str, a: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{a})"


def compare_ladder(ladders: dict[str, pd.DataFrame], colors: dict[str, str]) -> go.Figure:
    fig = go.Figure()
    for cat, lad in ladders.items():
        fig.add_trace(go.Scatter(
            x=lad["Kinh nghiệm"], y=lad["median"], mode="lines+markers", name=du.short(cat),
            line=dict(color=colors[cat], width=2.5), marker=dict(size=9, line=dict(color="white", width=2)),
            customdata=np.stack([lad["p25"], lad["p75"], lad["n"]], axis=-1),
            hovertemplate=f"<b>{cat}</b><br>%{{x}}: trung vị %{{y:.1f}} triệu"
                          "<br>P25–P75: %{customdata[0]:.1f}–%{customdata[1]:.1f}<br>n = %{customdata[2]:,}<extra></extra>",
            connectgaps=False,
        ))
        last = lad.dropna(subset=["median"]).tail(1)
        if not last.empty:
            fig.add_annotation(x=last["Kinh nghiệm"].iloc[0], y=last["median"].iloc[0],
                               text=f"{du.fmt_dec(last['median'].iloc[0])}", showarrow=False, xshift=22,
                               font=dict(size=12, color=INK))
    fig.update_yaxes(title_text="Lương trung vị (triệu VND/tháng)", rangemode="tozero")
    fig.update_xaxes(showgrid=False, title_text="Kinh nghiệm yêu cầu")
    return finish(fig, 400)


def experience_stack(dist: pd.DataFrame, order: list[str]) -> go.Figure:
    """Thanh 100% theo mức kinh nghiệm cho từng nhóm (màu xanh nhạt -> đậm theo thứ tự)."""
    fig = go.Figure()
    ylab = [du.short(c) for c in order]
    for exp, color in zip(du.EXPERIENCE_ORDER, ORDINAL5):
        d = dist[dist["Kinh nghiệm"] == exp].set_index("Nhóm nghề").reindex(order)
        fig.add_trace(go.Bar(
            y=ylab, x=d["% tin"], name=exp, orientation="h",
            marker=dict(color=color, line=dict(color="white", width=2)),
            text=[du.fmt_pct(v) if v >= 7 else "" for v in d["% tin"]], textposition="inside",
            insidetextanchor="middle", textfont=dict(color="white" if color in ORDINAL5[2:] else INK, size=12),
            customdata=d["Số tin"],
            hovertemplate="%{y} · " + exp + ": %{x:.1f}% (%{customdata:,} tin)<extra></extra>",
        ))
    fig.update_layout(barmode="stack", bargap=0.35, legend=dict(traceorder="normal"))
    fig.update_xaxes(range=[0, 100], ticksuffix="%", title_text="% số tin của nhóm nghề")
    fig.update_yaxes(autorange="reversed", showgrid=False)
    return finish(fig, max(220, 62 * len(order) + 110))


# ----------------------------------------------------------------------------
# 7. Gợi ý nghề: điểm cộng từng phần
# ----------------------------------------------------------------------------
def match_bars(scores: pd.DataFrame, labels: dict[str, str], top_k: int = 15) -> go.Figure:
    d = scores.head(top_k).iloc[::-1]
    fig = go.Figure()
    for (key, name), color in zip(labels.items(), CRITERIA_COLORS):
        if d[key].sum() <= 0:
            continue
        fig.add_trace(go.Bar(
            y=d["short"], x=d[key], name=name, orientation="h",
            marker=dict(color=color, line=dict(color="white", width=1.5)),
            hovertemplate="%{y} · " + name + ": +%{x:.1f} điểm<extra></extra>",
        ))
    fig.add_trace(go.Scatter(
        y=d["short"], x=d["score"], mode="text", text=[f"<b>{v:.0f}</b>" for v in d["score"]],
        textposition="middle right", textfont=dict(color=INK, size=12), showlegend=False, hoverinfo="skip",
    ))
    fig.update_layout(barmode="stack", bargap=0.3, legend=dict(traceorder="normal"))
    fig.update_xaxes(range=[0, max(100, d["score"].max() + 8)], title_text="Điểm phù hợp (0–100)")
    fig.update_yaxes(showgrid=False)
    return finish(fig, max(320, 30 * len(d) + 110))


# ----------------------------------------------------------------------------
# 8. Biểu đồ phân tích của TV2 (gọi lại hàm gốc, áp hệ màu chung)
# ----------------------------------------------------------------------------
def tv2_top_industries(jobs: pd.DataFrame, top_n: int = 10) -> go.Figure:
    top_n = max(1, min(top_n, jobs["category_clean"].nunique()))
    fig = tv2.chart_top_industries(jobs, top_n=top_n)
    fig.update_traces(marker=dict(color=BLUE, cornerradius=4), textfont=dict(color=INK2))
    fig.update_layout(coloraxis_showscale=False)
    fig.update_xaxes(range=None, autorange=True)
    return finish(fig, max(320, 40 * top_n + 100), "Số tin tuyển dụng theo nhóm nghề")


def tv2_salary_by_industry(jobs: pd.DataFrame, top_n: int = 10) -> go.Figure:
    top_n = max(1, min(top_n, jobs["category_clean"].nunique()))
    fig = tv2.chart_salary_by_industry_clean(jobs, top_n=top_n)
    fig.update_traces(marker_color=BLUE, line=dict(color=BLUE_DARK, width=1.5),
                      fillcolor=_alpha(BLUE, 0.25), boxpoints="outliers",
                      marker=dict(size=3, opacity=0.35, color=BLUE))
    fig.update_xaxes(title_text="Lương (triệu VND/tháng)")
    return finish(fig, max(360, 48 * top_n + 120), "Phân bố lương theo nhóm nghề")


def tv2_salary_by_experience(jobs: pd.DataFrame) -> go.Figure:
    fig = tv2.chart_salary_by_experience(jobs)
    for tr, c in zip(fig.data, ORDINAL5):
        tr.update(marker=dict(color=c, size=3, opacity=0.35), line=dict(color=c, width=1.5),
                  fillcolor=_alpha(c, 0.3), boxpoints="outliers")
    return finish(fig, 440, "Lương theo mức kinh nghiệm yêu cầu")


def tv2_experience_by_industry(jobs: pd.DataFrame, top_n: int = 8) -> go.Figure:
    top_n = max(1, min(top_n, jobs["category_clean"].nunique()))
    fig = tv2.chart_experience_by_industry(jobs, top_n=top_n)
    for tr, c in zip(fig.data, ORDINAL5):
        tr.update(marker=dict(color=c, line=dict(color="white", width=2)),
                  textfont=dict(color="white" if c in ORDINAL5[2:] else INK))
    fig = finish(fig, max(360, 52 * top_n + 140), "Tỷ trọng yêu cầu kinh nghiệm theo nhóm nghề")
    fig.update_layout(legend=dict(orientation="h", y=1.0, yanchor="bottom", x=0, title_text="", traceorder="normal"),
                      margin=dict(t=80))
    return fig


def tv2_skill_heatmap(skills: pd.DataFrame, jobs: pd.DataFrame, top_cats: int = 8, top_skills: int = 12) -> go.Figure:
    top_cats = max(1, min(top_cats, jobs["category_clean"].nunique()))
    fig = tv2.chart_skill_heatmap(skills, jobs, top_cats=top_cats, top_skills=top_skills)
    fig.update_traces(colorscale=SEQ_SCALE, xgap=2, ygap=2)
    fig.update_layout(coloraxis=dict(colorscale=SEQ_SCALE, colorbar=dict(title="% tin", ticksuffix="%")))
    fig = finish(fig, max(380, 46 * top_cats + 230), "Kỹ năng chuyên môn phổ biến theo nhóm nghề (% số tin)")
    fig.update_layout(margin=dict(b=120))
    return fig
