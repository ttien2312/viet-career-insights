"""
Module chứa các hàm vẽ biểu đồ của data_visualization.
Dành cho TV3 sử dụng trong ứng dụng Streamlit.

"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Cấu hình chung
COLORS = px.colors.qualitative.Set2
LAYOUT_BASE = dict(
    font=dict(family="Arial", size=13),
    plot_bgcolor='white',
    paper_bgcolor='white',
    margin=dict(l=10, r=10, t=60, b=10)
)

EXPERIENCE_ORDER = ["Không yêu cầu", "Dưới 1 năm", "1-2 năm", "3-4 năm", "Từ 5 năm"]


def style_fig(fig, title, height=500):
    """Hàm hỗ trợ định dạng giao diện chung cho biểu đồ."""
    fig.update_layout(
        **LAYOUT_BASE, 
        height=height,
        title=dict(text=title, font=dict(size=16))
    )
    return fig


def chart_top_industries(jobs_df, top_n=10):
    """Biểu đồ thanh ngang – Top ngành có nhiều tin nhất."""
    counts = jobs_df['category_clean'].value_counts().head(top_n).reset_index()
    counts.columns = ['Ngành nghề', 'Số tin']
    counts = counts.sort_values('Số tin')

    fig = px.bar(
        counts, x='Số tin', y='Ngành nghề', orientation='h',
        color='Số tin', color_continuous_scale='Blues', text='Số tin'
    )
    fig.update_traces(textposition='outside', textfont_size=11)
    style_fig(fig, f'Top {top_n} ngành nghề có nhu cầu tuyển dụng cao nhất', 520)
    fig.update_layout(
        xaxis_title='Số tin tuyển dụng',
        yaxis_title='',
        coloraxis_showscale=False,
        xaxis=dict(showgrid=True, gridcolor='#eeeeee'),
        yaxis=dict(showgrid=False)
    )
    return fig


def chart_salary_by_industry_clean(jobs_df, top_n=10):
    """Box plot – Phân bố lương theo ngành (không có chữ thống kê đè lên)."""
    col = 'salary_for_analysis'
    top_cats = jobs_df['category_clean'].value_counts().head(top_n).index.tolist()
    df = jobs_df[jobs_df['category_clean'].isin(top_cats)].dropna(subset=[col])

    order = df.groupby('category_clean')[col].median().sort_values().index.tolist()

    fig = px.box(
        df, x=col, y='category_clean', color='category_clean',
        category_orders={'category_clean': order},
        points='outliers', color_discrete_sequence=COLORS
    )

    fig.layout.annotations = []
    for trace in fig.data:
        if hasattr(trace, 'text'):
            trace.text = None
        if hasattr(trace, 'texttemplate'):
            trace.texttemplate = ""
        if hasattr(trace, 'hovertext'):
            trace.hovertext = None

    fig.update_layout(
        title=f'Phân bố lương theo {top_n} ngành chính (triệu VND/tháng)',
        xaxis_title='Lương trung vị (triệu VND)',
        yaxis_title='',
        height=640,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='#eeeeee', range=[0, 40])
    )
    return fig


def chart_experience_by_industry(jobs_df, top_n=8):
    """100% stacked bar – Tỷ trọng yêu cầu kinh nghiệm trong mỗi ngành."""
    top_cats = jobs_df['category_clean'].value_counts().head(top_n).index.tolist()
    df = jobs_df[jobs_df['category_clean'].isin(top_cats)]

    crosstab = pd.crosstab(df['category_clean'], df['experience_group'])
    crosstab = crosstab.reindex(columns=EXPERIENCE_ORDER, fill_value=0)
    pct = crosstab.div(crosstab.sum(axis=1), axis=0) * 100

    fig = go.Figure()
    colors = ['#e0f3db', '#ccebc5', '#a8ddb5', '#7bccc4', '#43a2ca'] 
    
    for i, exp in enumerate(EXPERIENCE_ORDER):
        text_labels = [f"{val:.0f}%" if val >= 5 else "" for val in pct[exp]]
        
        fig.add_trace(go.Bar(
            y=pct.index, 
            x=pct[exp], 
            name=exp,
            orientation='h', 
            text=text_labels,
            textposition='inside', 
            insidetextanchor='middle',
            marker_color=colors[i],
            marker_line=dict(width=0.5, color='white'),
            textfont=dict(size=11)
        ))
        
    fig.update_layout(barmode='stack')
    style_fig(fig, 'Tỷ trọng yêu cầu kinh nghiệm theo ngành (%)', 560)
    fig.update_layout(
        xaxis_title='% tin trong ngành', 
        xaxis=dict(range=[0, 100], showgrid=False),
        yaxis_title='', 
        legend=dict(
            orientation='h', 
            y=-0.15, 
            title="Mức độ kinh nghiệm:",
            traceorder='normal'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    return fig


def chart_top_locations(jobs_df, top_n=12):
    """Bar chart – Top tỉnh/thành có nhiều tin nhất."""
    exploded = jobs_df['location_clean'].dropna().str.split(' \\| ').explode()
    counts = exploded.value_counts().head(top_n).reset_index()
    counts.columns = ['Địa điểm', 'Số tin']
    counts = counts.sort_values('Số tin')

    fig = px.bar(
        counts, x='Số tin', y='Địa điểm', orientation='h',
        color='Số tin', color_continuous_scale='Teal', text='Số tin'
    )
    fig.update_traces(textposition='outside')
    
    fig.update_layout(
        title=f'Top {top_n} địa điểm có nhu cầu tuyển dụng cao nhất',
        height=520,
        font=dict(family="Arial", size=13),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=10, r=10, t=60, b=10),
        xaxis_title='Số tin tuyển dụng',
        yaxis_title='',
        coloraxis_showscale=False,
        yaxis=dict(showgrid=False)
    )
    
    fig.update_xaxes(
        tickvals=[0, 5000, 10000, 15000, 20000],
        ticktext=['0', '5000', '10000', '15000', '20000'],
        range=[0, 23000],
        showgrid=True, 
        gridcolor='#eeeeee'
    )
    return fig


def chart_skill_heatmap(skills_df, jobs_df, top_cats=8, top_skills=12):
    """Heatmap – Tỷ lệ xuất hiện kỹ năng chuyên môn phổ biến theo ngành."""
    tech = skills_df[skills_df['skill_type'] == 'Kỹ năng chuyên môn'].copy()
    top_cat_list = jobs_df['category_clean'].value_counts().head(top_cats).index.tolist()
    tech_cat = tech[tech['category_clean'].isin(top_cat_list)]

    top_skill_list = tech_cat['skill'].value_counts().head(top_skills).index.tolist()

    filtered = tech_cat[tech_cat['skill'].isin(top_skill_list)]
    pivot = filtered.groupby(['category_clean', 'skill']).size().unstack(fill_value=0)
    for s in top_skill_list:
        if s not in pivot.columns:
            pivot[s] = 0
    pivot = pivot[top_skill_list]

    total_jobs_by_cat = jobs_df[jobs_df['category_clean'].isin(top_cat_list)] \
        .groupby('category_clean').size()
    pct = pivot.div(total_jobs_by_cat, axis=0) * 100

    fig = px.imshow(
        pct.values, x=pct.columns, y=pct.index, aspect='auto',
        color_continuous_scale='YlOrRd', text_auto='.1f',
        labels=dict(x='Kỹ năng', y='Ngành', color='% trong ngành')
    )
    style_fig(fig, 'Tỷ lệ xuất hiện kỹ năng chuyên môn phổ biến theo ngành (%)', 560)
    fig.update_layout(xaxis=dict(tickangle=-40))
    return fig


def chart_salary_by_experience(jobs_df):
    """Box plot – Mức lương tăng theo số năm kinh nghiệm."""
    df = jobs_df.dropna(subset=['salary_for_analysis', 'experience_group']).copy()
    df = df[df['experience_group'].isin(EXPERIENCE_ORDER)]

    fig = px.box(
        df, x='experience_group', y='salary_for_analysis',
        color='experience_group',
        category_orders={'experience_group': EXPERIENCE_ORDER},
        color_discrete_sequence=COLORS, points='outliers'
    )

    style_fig(fig, 'Mức lương theo nhóm kinh nghiệm (triệu VND/tháng)', 560)
    fig.update_layout(
        xaxis_title='Nhóm kinh nghiệm',
        yaxis_title='Lương (triệu VND)',
        showlegend=False,
        yaxis=dict(range=[0, 40], showgrid=True, gridcolor='#eeeeee'),
        annotations=[] 
    )
    return fig


# ==========================================
# HÀM RÚT RA NHẬN XÉT (Dành cho TV3/TV4)
# ==========================================
def build_findings(jobs_df, skills_df):
    """Trả về danh sách các phát hiện chính kèm số liệu."""
    findings = []
    total = len(jobs_df)

    top = jobs_df['category_clean'].value_counts()
    findings.append(
        f"F1. 3 ngành dẫn đầu (Kinh doanh, Sản xuất, Marketing) chiếm "
        f"{top.head(3).sum()/total*100:.1f}% tổng tin "
        f"({top.head(3).sum():,}/{total:,})."
    )

    med_all = jobs_df['salary_for_analysis'].median()
    p25 = jobs_df['salary_for_analysis'].quantile(.25)
    p75 = jobs_df['salary_for_analysis'].quantile(.75)
    findings.append(
        f"F2. Lương trung vị toàn thị trường: {med_all:.1f} triệu; "
        f"khoảng liên tứ phân vị {p25:.1f}–{p75:.1f} triệu."
    )

    cat_med = jobs_df.groupby('category_clean')['salary_for_analysis'] \
                    .median().sort_values(ascending=False)
    findings.append(
        f"F3. Ngành có lương trung vị cao nhất: {cat_med.index[0]} "
        f"({cat_med.iloc[0]:.1f} triệu) – cao nhất trong {cat_med.notna().sum()} ngành."
    )

    med_by_exp = jobs_df.groupby('experience_group')['salary_for_analysis'].median()
    ratio = med_by_exp.get('Từ 5 năm', np.nan) / med_by_exp.get('Không yêu cầu', np.nan)
    findings.append(
        f"F4. Người có ≥5 năm kinh nghiệm có lương trung vị gấp {ratio:.1f} lần "
        f"người không yêu cầu kinh nghiệm."
    )

    loc = jobs_df['location_clean'].dropna().str.split(' \\| ').explode()
    top2_share = loc.value_counts().head(2).sum() / len(jobs_df) * 100
    findings.append(
        f"F5. Hà Nội và TP.HCM chiếm {top2_share:.1f}% nhu cầu tuyển dụng "
        f"– mức độ tập trung địa lý rất cao."
    )

    tech = skills_df[skills_df['skill_type'] == 'Kỹ năng chuyên môn']
    top_skill = tech['skill'].value_counts().head(1)
    findings.append(
        f"F6. Kỹ năng chuyên môn xuất hiện nhiều nhất: '{top_skill.index[0]}' "
        f"({top_skill.iloc[0]:,} lượt) – kỹ năng phổ quát cần trang bị sớm."
    )
    return findings