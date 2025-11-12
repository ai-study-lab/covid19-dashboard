import streamlit as st
import pandas as pd

# 화면 세팅
st.set_page_config(page_title="백신 접종 현황",
                   page_icon="💊")
st.header('백신 접종 현황')

# 데이터 조회
df = pd.read_csv("data/WHO-COVID-19-global-data-latlon.csv")

# 위도 값이 0인 데이타는 제외함
df = df[df["latitude"] != 0]

# 원 크기 세팅
df["map_circle_size"] = df["New_cases"]/20  # 대충 20으로 나눴을 때 크기가 적당히 나오는것 같당

# 색깔 세팅
color_map = {"AFRICA":"#ED1C2480", 
             "ASIA":"#EDDB1680", 
             "EUROPE":"#1518ED80", 
             "NORTH_AMERICA":"#ED8EE280", 
             "OCEANIA":"#8AEDB580", 
             "SOUTH_AMERICA":"#aaff0080"}
df["color"] = df["continent"].replace(color_map)

# 국가별로 groupby 처리
df_groupby = df.groupby("Country_code").max()

# 지도 그리기
st.map(df_groupby, latitude="latitude", longitude="longitude", size="map_circle_size", color="color", zoom=1)
