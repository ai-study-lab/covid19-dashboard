import streamlit as st
import pydeck as pdk
import pandas as pd

# 화면 세팅
st.set_page_config(page_title="백신 접종 현황",
                   page_icon="💊")
st.header('백신 접종 현황')

# 데이터 조회
df = pd.read_csv("data/COV_VAC_2021_2023_latlon.csv")
df["map_circle_size"] = df["총 1차 접종자 수"]/1000
df["vaccinated_count"] = df["총 1차 접종자 수"]

color_map = {"AFRICA":[255, 253, 85], 
             "ASIA":[224, 125, 255], 
             "EUROPE":[89, 255, 88], 
             "NORTH_AMERICA":[128, 123, 255], 
             "OCEANIA":[255, 82, 69], 
             "SOUTH_AMERICA":[54, 126, 127]}
df["color"] = df["AREA"].map(color_map)

# 지역별 접종 현황
st.subheader('지역별 백신 접종 현황')
df_groupby = df.groupby("COUNTRY_CD").max()
#st.map(df_groupby, latitude="latitude", longitude="longitude", size="map_circle_size", color="color", zoom=1)

# ScatterplotLayer 생성
layer = pdk.Layer(
    'ScatterplotLayer',
    data=df_groupby,
    get_position='[longitude, latitude]',  # 올바른 컬럼명 사용
    get_radius='map_circle_size',         # 컬럼명으로 반지름 지정
    get_fill_color='color',     # 주황색
    pickable=True,
    opacity=0.5,
    radiusScale=2,               # radiusScale 값 조정
    radiusMinPixels=5            # radiusMinPixels 값 조정
)

# 뷰 설정
view_state = pdk.ViewState(latitude=35.9, longitude=14.1, zoom=1)

# 렌더링
r = pdk.Deck(
    layers=[layer], 
    initial_view_state=view_state,
    tooltip={"text": "{COUNTRY_NM} : {vaccinated_count}명"},
    )
st.pydeck_chart(r)

# 국가별 접종 현황
st.subheader('국가별 백신 접종 현황')
# 지역 selectbox
areas = list(df.groupby("AREA").groups.keys())
selected_area = st.selectbox(
    "대륙을 선택하세요.",
    areas
)
# 국가 selectbox
nations = list(df[df["AREA"] == selected_area].groupby("COUNTRY_NM").groups.keys())
selected_nation = st.selectbox(
    "국가을 선택하세요.",
    nations
)
vaccine_by_nation = df[df["COUNTRY_NM"] == selected_nation]
st.line_chart(data=vaccine_by_nation, x="DATE", y=["총 1차 접종자 수", "총 부스터 접종자 수"])
st.dataframe(vaccine_by_nation)