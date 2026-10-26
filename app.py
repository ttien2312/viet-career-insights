
import pandas as pd
import streamlit as st

# =========================
# 1. CẤU HÌNH TRANG
# =========================
st.set_page_config(
    page_title="Viet Career Insights",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Viet Career Insights")
st.subheader("Khám phá nghề nghiệp theo thị trường lao động Việt Nam")
st.write(
    "Demo bước đầu dành cho học sinh THPT tìm hiểu các nhóm nghề, "
    "địa điểm làm việc và yêu cầu kinh nghiệm."
)

# =========================
# 2. DỮ LIỆU MẪU
# =========================
data = [
    {
        "Nghề nghiệp": "Data Analyst",
        "Nhóm nghề": "Dữ liệu & AI",
        "Địa điểm": "Hà Nội",
        "Kinh nghiệm (năm)": 0,
        "Lương (triệu/tháng)": 12
    },
    {
        "Nghề nghiệp": "Machine Learning Engineer",
        "Nhóm nghề": "Dữ liệu & AI",
        "Địa điểm": "TP. Hồ Chí Minh",
        "Kinh nghiệm (năm)": 2,
        "Lương (triệu/tháng)": 25
    },
    {
        "Nghề nghiệp": "Data Scientist",
        "Nhóm nghề": "Dữ liệu & AI",
        "Địa điểm": "Hà Nội",
        "Kinh nghiệm (năm)": 2,
        "Lương (triệu/tháng)": 22
    },
    {
        "Nghề nghiệp": "Software Engineer",
        "Nhóm nghề": "Công nghệ phần mềm",
        "Địa điểm": "Hà Nội",
        "Kinh nghiệm (năm)": 1,
        "Lương (triệu/tháng)": 16
    },
    {
        "Nghề nghiệp": "Web Developer",
        "Nhóm nghề": "Công nghệ phần mềm",
        "Địa điểm": "Đà Nẵng",
        "Kinh nghiệm (năm)": 0,
        "Lương (triệu/tháng)": 10
    },
    {
        "Nghề nghiệp": "Backend Developer",
        "Nhóm nghề": "Công nghệ phần mềm",
        "Địa điểm": "TP. Hồ Chí Minh",
        "Kinh nghiệm (năm)": 3,
        "Lương (triệu/tháng)": 24
    },
    {
        "Nghề nghiệp": "UI/UX Designer",
        "Nhóm nghề": "Thiết kế",
        "Địa điểm": "Hà Nội",
        "Kinh nghiệm (năm)": 1,
        "Lương (triệu/tháng)": 14
    },
    {
        "Nghề nghiệp": "Graphic Designer",
        "Nhóm nghề": "Thiết kế",
        "Địa điểm": "Đà Nẵng",
        "Kinh nghiệm (năm)": 0,
        "Lương (triệu/tháng)": 9
    },
    {
        "Nghề nghiệp": "Digital Marketing Specialist",
        "Nhóm nghề": "Marketing",
        "Địa điểm": "TP. Hồ Chí Minh",
        "Kinh nghiệm (năm)": 1,
        "Lương (triệu/tháng)": 13
    },
    {
        "Nghề nghiệp": "Content Marketing",
        "Nhóm nghề": "Marketing",
        "Địa điểm": "Hà Nội",
        "Kinh nghiệm (năm)": 0,
        "Lương (triệu/tháng)": 9
    },
    {
        "Nghề nghiệp": "Financial Analyst",
        "Nhóm nghề": "Tài chính",
        "Địa điểm": "TP. Hồ Chí Minh",
        "Kinh nghiệm (năm)": 2,
        "Lương (triệu/tháng)": 18
    },
    {
        "Nghề nghiệp": "Accountant",
        "Nhóm nghề": "Tài chính",
        "Địa điểm": "Đà Nẵng",
        "Kinh nghiệm (năm)": 3,
        "Lương (triệu/tháng)": 13
    },
]

df = pd.DataFrame(data)

# =========================
# 3. BỘ LỌC TƯƠNG TÁC
# =========================
st.sidebar.header("🔎 Bộ lọc nghề nghiệp")

categories = ["Tất cả"] + sorted(df["Nhóm nghề"].unique().tolist())
locations = ["Tất cả"] + sorted(df["Địa điểm"].unique().tolist())
experience_options = [
    "Tất cả",
    "Không yêu cầu kinh nghiệm",
    "0–1 năm",
    "2–3 năm",
    "4 năm trở lên"
]

selected_category = st.sidebar.selectbox(
    "Nhóm nghề",
    categories
)

selected_location = st.sidebar.selectbox(
    "Địa điểm",
    locations
)

selected_experience = st.sidebar.selectbox(
    "Kinh nghiệm",
    experience_options
)

# =========================
# 4. LỌC DỮ LIỆU
# =========================
filtered_df = df.copy()

if selected_category != "Tất cả":
    filtered_df = filtered_df[
        filtered_df["Nhóm nghề"] == selected_category
    ]

if selected_location != "Tất cả":
    filtered_df = filtered_df[
        filtered_df["Địa điểm"] == selected_location
    ]

if selected_experience == "Không yêu cầu kinh nghiệm":
    filtered_df = filtered_df[
        filtered_df["Kinh nghiệm (năm)"] == 0
    ]
elif selected_experience == "0–1 năm":
    filtered_df = filtered_df[
        filtered_df["Kinh nghiệm (năm)"].between(0, 1)
    ]
elif selected_experience == "2–3 năm":
    filtered_df = filtered_df[
        filtered_df["Kinh nghiệm (năm)"].between(2, 3)
    ]
elif selected_experience == "4 năm trở lên":
    filtered_df = filtered_df[
        filtered_df["Kinh nghiệm (năm)"] >= 4
    ]

# =========================
# 5. HIỂN THỊ KẾT QUẢ
# =========================
col1, col2 = st.columns(2)

with col1:
    st.metric("Số nghề phù hợp", len(filtered_df))

with col2:
    if not filtered_df.empty:
        avg_salary = filtered_df["Lương (triệu/tháng)"].mean()
        st.metric("Lương trung bình mẫu", f"{avg_salary:.1f} triệu/tháng")
    else:
        st.metric("Lương trung bình mẫu", "Chưa có dữ liệu")

st.subheader("📋 Danh sách nghề nghiệp phù hợp")

if filtered_df.empty:
    st.warning(
        "Không tìm thấy nghề phù hợp với các bộ lọc. "
        "Hãy thử thay đổi lựa chọn."
    )
else:
    st.dataframe(
        filtered_df.reset_index(drop=True),
        use_container_width=True,
        hide_index=True
    )

st.caption(
    "Lưu ý: Đây là dữ liệu giả lập để kiểm tra giao diện, "
    "không phải số liệu tuyển dụng thực tế."
)
