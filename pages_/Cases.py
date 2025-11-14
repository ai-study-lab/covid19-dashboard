import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="2021년 확진자 현황", page_icon="💊", layout="wide")

tab1, tab2, tab3 = st.tabs(
    ["확진자 현황", "사망자 현황", "백신 접종 현황"]
)
with tab1:
    st.header("확진자 현황")
    # 데이터 로드 및 2021년 필터링 
    df = pd.read_csv("WHO-COVID-19-global-data-latlon.csv")
    df['Date_reported'] = pd.to_datetime(df['Date_reported'])

    # 2021년, 위도 0이 아닌 데이터만 필터링
    df_base = df[
        (df["latitude"] != 0) &
        (df['Date_reported'].dt.year == 2021)
    ].copy()

    # 사이드바: 지역 선택 및 날짜 범위 선택
    st.sidebar.header("필터 설정")

    regions = ['전체'] + df_base['continent'].dropna().unique().tolist()
    selected_region = st.sidebar.selectbox("지역 선택", regions)

    # 날짜 범위 슬라이더
    min_date = df_base['Date_reported'].min().date()
    max_date = df_base['Date_reported'].max().date()
    selected_date_range = st.sidebar.slider(
        "날짜 범위 선택",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="YYYY-MM-DD"
    )

    # 필터 적용
    df_filtered = df_base.copy()

    # 지역 필터
    if selected_region != '전체':
        df_filtered = df_filtered[df_filtered['continent'] == selected_region]

    # 날짜 필터
    df_filtered = df_filtered[
        (df_filtered['Date_reported'].dt.date >= selected_date_range[0]) &
        (df_filtered['Date_reported'].dt.date <= selected_date_range[1])
    ].copy()

    # 확진자 유형 선택 토글 
    st.title("2021년 확진자 현황 대시보드")

    case_type = st.radio("확진자 유형 선택", ['신규 확진자', '누적 확진자'], horizontal=True)


    # 지도
    st.subheader("🌍 지도 시각화")

    if case_type == '신규 확진자':
        # 국가, 위도, 경도, 대륙별 신규 확진자 합산
        map_data = df_filtered.groupby(
            ['Country_code', 'latitude', 'longitude', 'continent'], as_index=False
        )['New_cases'].sum().rename(columns={'New_cases': 'Cases'})
    else:
        # 누적 확진자
        idx_latest = df_filtered.groupby('Country_code')['Date_reported'].idxmax()
        map_data = df_filtered.loc[idx_latest, ['Country_code', 'latitude', 'longitude', 'continent', 'Cumulative_cases']]
        map_data = map_data.rename(columns={'Cumulative_cases': 'Cases'})

    # 원 크기 조절 
    map_data['map_circle_size'] = map_data['Cases'] / 20

    # 대륙별 색상 매핑 
    color_map = {
        "AFRICA": "#ED1C2480",
        "ASIA": "#EDDB1680",
        "EUROPE": "#1518ED80",
        "NORTH_AMERICA": "#ED8EE280",
        "OCEANIA": "#8AEDB580",
        "SOUTH_AMERICA": "#aaff0080"
    }
    map_data['continent_upper'] = map_data['continent'].str.upper()
    map_data['color'] = map_data['continent_upper'].map(color_map)

    st.map(
        map_data,
        latitude="latitude",
        longitude="longitude",
        size="map_circle_size",
        color="color",
        zoom=1
    )

    # 추세 그래프
    st.subheader("📈 국가별 확진자 추세 그래프")
    countries = ['선택 안 함'] + df_filtered['Country'].unique().tolist()
    selected_country = st.selectbox("국가 선택", countries)

    if selected_country != '선택 안 함':
        country_df = df_filtered[df_filtered['Country'] == selected_country].copy()

        y_col = 'New_cases' if case_type == '신규 확진자' else 'Cumulative_cases'

        chart = alt.Chart(country_df).mark_line(point=True).encode(
            x=alt.X('Date_reported:T', title='날짜'),
            y=alt.Y(f'{y_col}:Q', title=f"{selected_country} {case_type}"),
            tooltip=['Date_reported:T', alt.Tooltip(f'{y_col}:Q', title=case_type)]
        ).properties(
            title=f"{selected_country} {case_type} 추세"
        ).interactive()

        st.altair_chart(chart, use_container_width=True)


with tab2:
    st.header("사망자 현황")
    
with tab3:
    st.header("백신 접종 현황")
