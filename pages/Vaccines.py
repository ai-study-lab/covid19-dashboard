import streamlit as st
import pydeck as pdk
import pandas as pd

# 화면 세팅
st.set_page_config(page_title="백신 접종 현황",
                   page_icon="💊")
st.header('백신 접종 현황')

# 데이터 조회
df = pd.read_csv("data/WHO-COVID-19-global-data-latlon.csv")

# 위도 값이 0인 데이타는 제외함
df = df[df["latitude"] != 0]

df["map_circle_size"] = df["New_cases"]/50

color_map = {"AFRICA":[255, 253, 85], 
             "ASIA":[224, 125, 255], 
             "EUROPE":[89, 255, 88], 
             "NORTH_AMERICA":[128, 123, 255], 
             "OCEANIA":[255, 82, 69], 
             "SOUTH_AMERICA":[54, 126, 127]}
df["color"] = df["continent"].map(color_map)

df_groupby = df.groupby("Country_code").max()

# ScatterplotLayer 생성
layer = pdk.Layer(
    'ScatterplotLayer',
    data=df_groupby,
    get_position='[longitude, latitude]',
    get_radius='map_circle_size',# 컬럼명으로 반지름 지정
    get_fill_color='color',
    pickable=True,
    opacity=0.3,
    radiusScale=2,               # radiusScale 값 조정
    radiusMinPixels=5            # radiusMinPixels 값 조정
)

# 뷰 설정
view_state = pdk.ViewState(latitude=35.9, longitude=14.1, zoom=1)

# 렌더링
r = pdk.Deck(
        layers=[layer], 
        map_style=None,
        initial_view_state=view_state,
        tooltip={"text": "{Country} : {New_cases}명"},
    )
st.pydeck_chart(r)