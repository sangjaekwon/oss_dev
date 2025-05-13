  import streamlit as st
import pandas as pd
import plotly.express as px

# ---- 데이터 로딩 ----
@st.cache_data
def load_data():
    df = pd.read_csv("accident_stats.csv", encoding="cp949")  # 인코딩 주의
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
injury_df = filtered[["시군구", "중상자수", "경상자수", "부상신고자수"]].melt(id_vars="시군구", var_name="부상자유형", value_name="인원수")
injury_chart = px.bar(injury_df, x="시군구", y="인원수", color="부상자유형", barmode="group", title="시군구별 부상자 유형 비교")
st.plotly_chart(injury_chart)

# ---- 시도별 사고 추이 (월별) ----
st.subheader("📈 월별 사고 추이")
monthly_trend = df[df["시도"].isin(selected_sido)].groupby(["년도", "월"])["발생건수"].sum().reset_index()
line = px.line(monthly_trend, x="월", y="발생건수", color="년도", title="월별 발생건수 추이")
st.plotly_chart(line)
