import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static

# ---- 데이터 로딩 ----
@st.cache_data
def load_data():
    df = pd.read_csv("accident_stats.csv", encoding="utf-8")
    return df

df = load_data()

# ---- 전처리 ----
df.columns = df.columns.str.strip()
df = df.rename(columns={
    "발생년": "년도", "발생월": "월",
    "발생건수": "발생건수",
    "사망자수": "사망자수",
    "중상자수": "중상자수",
    "경상자수": "경상자수",
    "부상신고자수": "부상신고자수"
})

# ---- 사이드바 필터 ----
st.sidebar.header("🧪 필터 설정")
selected_year = st.sidebar.selectbox("년도", sorted(df["년도"].unique()))
selected_month = st.sidebar.selectbox("월", sorted(df["월"].unique()))
selected_sido = st.sidebar.multiselect("시도", df["시도"].unique(), default=["서울특별시"])

# ---- 필터 적용 ----
filtered = df[
    (df["년도"] == selected_year) &
    (df["월"] == selected_month) &
    (df["시도"].isin(selected_sido))
]

st.title("🚧 시도/시군구별 교통사고 통계 분석")
st.write(f"▶️ {selected_year}년 {selected_month}월 / 선택된 지역: {', '.join(selected_sido)}")

# ---- 데이터 표 ----
st.subheader("📋 사고 통계 테이블")
st.dataframe(filtered)

# ---- 시군구별 사고 발생 건수 ----
st.subheader("📊 시군구별 사고 발생건수")
bar = px.bar(filtered, x="시군구", y="발생건수", color="시도", title="시군구별 사고 발생건수")
st.plotly_chart(bar)

# ---- 시군구별 부상자 유형 비교 ----
st.subheader("🤕 부상자 유형 비교")
injury_df = filtered[["시군구", "중상자수", "경상자수", "부상신고자수"]].melt(
    id_vars="시군구", var_name="부상자유형", value_name="인원수"
)
injury_chart = px.bar(injury_df, x="시군구", y="인원수", color="부상자유형", barmode="group", title="시군구별 부상자 유형 비교")
st.plotly_chart(injury_chart)

# ---- 시도별 사고 추이 (월별) ----
st.subheader("📈 월별 사고 추이")
monthly_trend = df[df["시도"].isin(selected_sido)].groupby(["년도", "월"])["발생건수"].sum().reset_index()
line = px.line(monthly_trend, x="월", y="발생건수", color="년도", title="월별 발생건수 추이")
st.plotly_chart(line)

# ---- 지도 시각화 ----
st.subheader("🗺️ 사고 건수 지도 시각화 (서울 일부)")

# 서울 일부 시군구 좌표
location_data = {
    '종로구': [37.5729503, 126.9793579],
    '중구': [37.5638439, 126.997602],
    '용산구': [37.5324275, 126.990146],
    '성동구': [37.550978, 127.040580],
    '광진구': [37.538484, 127.082293],
    '동대문구': [37.574368, 127.039569],
    '중랑구': [37.606991, 127.092789],
    '성북구': [37.589400, 127.016637],
    '강북구': [37.646995, 127.014573],
}

map_center = [37.5665, 126.9780]
m = folium.Map(location=map_center, zoom_start=11)

for _, row in filtered.iterrows():
    sigungu = row["시군구"]
    count = row["발생건수"]
    if sigungu in location_data:
        lat, lon = location_data[sigungu]
        folium.CircleMarker(
            location=[lat, lon],
            radius=min(count / 5, 20),
            popup=f"{sigungu}: {count}건",
            color='crimson',
            fill=True,
            fill_color='crimson'
        ).add_to(m)

folium_static(m)
