import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static
import chardet

# ---- 데이터 로딩 ----
@st.cache_data
def load_data():
    # 인코딩 자동 감지
    with open("accident_stats.csv", "rb") as f:
        result = chardet.detect(f.read())
        encoding = result["encoding"]
    
    df = pd.read_csv("accident_stats.csv", encoding=encoding)
    
    # 컬럼명 전처리 (여기서는 공백 제거)
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# ---- 사이드바 필터 ----
st.sidebar.header("🧪 필터 설정")
selected_sido = st.sidebar.multiselect("시도", df["시도"].unique())

# ---- 필터 적용 ----
filtered = df[df["시도"].isin(selected_sido)]  # 선택한 시도에 맞는 데이터 필터링

st.title("🚧 시도/시군구별 교통사고 통계 분석")
st.write(f"▶️ 선택된 시도: {', '.join(selected_sido)}")

# ---- 데이터 표 ----
st.subheader("📋 사고 통계 테이블")
st.dataframe(filtered)

# ---- 시군구별 사고 발생 건수 ----
st.subheader("📊 시군구별 사고 발생건수")
bar = px.bar(filtered, x="시군구", y="사고건수", color="시도", title="시군구별 사고 발생건수")
st.plotly_chart(bar)

# ---- 시군구별 부상자 유형 비교 ----
st.subheader("🤕 부상자 유형 비교")
injury_df = filtered[["시군구", "중상자수", "경상자수", "부상신고자수"]].melt(
    id_vars="시군구", var_name="부상자유형", value_name="인원수"
)
injury_chart = px.bar(injury_df, x="시군구", y="인원수", color="부상자유형", barmode="group", title="시군구별 부상자 유형 비교")
st.plotly_chart(injury_chart)

# ---- 지도 시각화 ----
st.subheader("🗺️ 사고 건수 지도 시각화 (대한민국 전체)")

# 대한민국 시군구 좌표 (시도별 대략적인 좌표 예시)
location_data = {
    # 서울
    '종로구': [37.5729503, 126.9793579],
    '중구': [37.5638439, 126.997602],
    '용산구': [37.5324275, 126.990146],
    '성동구': [37.550978, 127.040580],
    '광진구': [37.538484, 127.082293],
    '동대문구': [37.574368, 127.039569],
    '중랑구': [37.606991, 127.092789],
    '성북구': [37.589400, 127.016637],
    '강북구': [37.646995, 127.014573],
    
    # 부산
    '부산': [35.1796, 129.0756],
    
    # 대구
    '대구': [35.8702, 128.6025],
    
    # 인천
    '인천': [37.4563, 126.7052],
    
    # 광주
    '광주': [35.1595, 126.8526],
    
    # 대전
    '대전': [36.3504, 127.3845],
    
    # 울산
    '울산': [35.5384, 129.3114],
    
    # 경기
    '수원시': [37.2636, 127.0286],
    '고양시': [37.6584, 126.8320],
    '용인시': [37.2412, 127.1780],
    '성남시': [37.4384, 127.1371],
    
    # 강원
    '춘천': [37.8756, 127.7308],
    
    # 충북
    '청주': [36.6352, 127.4912],
    
    # 충남
    '천안': [36.8195, 127.1139],
    
    # 전북
    '전주': [35.8255, 127.1502],
    
    # 전남
    '광양': [34.9504, 127.7004],
    
    # 경북
    '경산': [35.8280, 128.7387],
    
    # 경남
    '창원': [35.2288, 128.6817],
    
    # 제주
    '제주': [33.4996, 126.5312]
}

map_center = [36.5, 127.5]  # 대한민국의 대략적인 중심
m = folium.Map(location=map_center, zoom_start=7)

# 사고 건수에 따른 마커 추가
for _, row in filtered.iterrows():
    sigungu = row["시군구"]
    count = row["사고건수"]
    if sigungu in location_data:
        lat, lon = location_data[sigungu]
        folium.CircleMarker(
            location=[lat, lon],
            radius=min(count / 5, 20),  # 사고 건수가 클수록 큰 마커
            popup=f"{sigungu}: {count}건",
            color='crimson',
            fill=True,
            fill_color='crimson'
        ).add_to(m)

folium_static(m)
