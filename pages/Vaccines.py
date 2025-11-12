import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 화면 세팅
st.set_page_config(page_title="백신 접종 현황",
                   page_icon="💊")
st.header('백신 접종 현황')

# 데이터 조회
df = pd.read_csv("data/COV_VAC_2021_2023_latlon.csv")
df["map_circle_size"] = df["총 1차 접종자 수"]/300

color_map = {"AFRICA":"#ED1C2480", "ASIA":"#EDDB1680", "EUROPE":"#1518ED80", "NORTH_AMERICA":"#ED8EE280", "OCEANIA":"#8AEDB580", "SOUTH_AMERICA":"#aaff0080"}
df["color"] = df["AREA"].replace(color_map)

# 지역별 접종 현황
st.subheader('지역별 백신 접종 현황')
df_groupby = df.groupby("COUNTRY_CD").max()
st.map(df_groupby, latitude="latitude", longitude="longitude", size="map_circle_size", color="color", zoom=1)

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