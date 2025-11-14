import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(layout="wide")
st.title("코로나 대시보드")

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
    @st.cache_data 
    def load_data(file_path):
        try:
            df = pd.read_csv(file_path)
            df['날짜'] = pd.to_datetime(df['날짜'])
            df = df.sort_values(by='날짜')
            return df
        except FileNotFoundError:
            st.error(f"❌ 오류: 파일을 찾을 수 없습니다. 경로를 확인하세요: {file_path}")
            return None
        except Exception as e:
            st.error(f"데이터 로드 또는 '날짜' 변환 중 오류: {e}")
            return None

    YOUR_CSV_FILE = "WHO-COVID-19-korean.csv"  
    df = load_data(YOUR_CSV_FILE)

    st.title(' 전 세계 현황 대시보드')

    # 데이터가 성공적으로 로드되었는지 확인
    if df is not None:
        
        # 가장 최신 날짜의 데이터 (맵, 테이블, 메트릭 등에서 사용)
        latest_date = df['날짜'].max()
        latest_data = df[df['날짜'] == latest_date]

        st.success(f"✅ 데이터 로드 성공! (최신 데이터 기준일: {latest_date.strftime('%Y-%m-%d')})")
        
        # 시각화 1: 맵
        st.subheader('국가별 최신 누적 사망자 맵') 
        
        view_state = pdk.ViewState(
            latitude=latest_data['위도'].mean(),
            longitude=latest_data['경도'].mean(),
            zoom=0, pitch=0
        )
        layer = pdk.Layer(
            'ScatterplotLayer',
            data=latest_data,
            get_position='[경도, 위도]',
            get_color='[200, 30, 0, 160]',
            get_radius='누적사망자 * 1 + 50', # (스케일 조절 필요)
            pickable=True
        )
        tooltip = {
            "html": "<b>{국가} ({대륙})</b><br/>"
                    "신규 사망자: {신규_사망자}<br/>"
                    "누적 사망자: {누적_사망자}",
            "style": { "backgroundColor": "steelblue", "color": "white" }
        }
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v9',
            initial_view_state=view_state,
            layers=[layer],
            tooltip=tooltip
        ))

        # 최근 동향 대시보드 (신규 사망자 기준)
        st.subheader('최근 동향 (신규 사망자 기준)')
        
        # 라디오 버튼으로 기간 선택
        period = st.radio(
            "분석할 최근 기간을 선택하세요:",
            (7, 14, 28),
            index=2, # 기본값으로 28일 선택
            horizontal=True
        )
        
        # 선택된 기간에 해당하는 데이터 필터링
        start_date = latest_date - pd.Timedelta(days=period - 1)
        recent_df = df[df['날짜'] >= start_date]
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**최근 {period}일간 전 세계 신규 사망자 추이**")
            # 날짜별 신규 사망자 합계
            recent_trend = recent_df.groupby('날짜')['신규_사망자'].sum()
            st.area_chart(recent_trend)
            
        with col2:
            st.write(f"**최근 {period}일간 신규 사망자 상위 10개국**")
            # 국가별 신규 사망자 합계
            recent_top10 = recent_df.groupby('국가')['신규_사망자'].sum().nlargest(10)
            st.bar_chart(recent_top10)

        st.markdown("---")
        
        # 5. 특정 국가 상세 분석 
        st.subheader('특정 국가 상세')
        
        # 국가 선택을 위한 드롭다운 메뉴 (selectbox)
        # '전체' 옵션을 맨 앞에 추가
        country_list = ['전체'] + sorted(df['국가'].unique())
        selected_country = st.selectbox('분석할 국가를 선택하세요:', country_list)
        
        if selected_country == '전체':
            st.info('왼쪽 드롭다운 메뉴에서 특정 국가를 선택하면 상세 데이터를 볼 수 있습니다.')
            
            # 전 세계 누적 현황 차트 (국가 '전체'일 때만 표시)
            st.subheader('🌍 전 세계 누적 현황')
            col1, col2 = st.columns(2)
            with col1:
                st.write("**날짜별 전 세계 누적 사망자 추이**")
                time_series_data = df.groupby('날짜')['누적_사망자'].sum()
                st.line_chart(time_series_data)
            with col2:
                st.write("**대륙별 누적 사망자 (최신)**")
                continent_data = latest_data.groupby('대륙')['누적_사망자'].sum()
                st.bar_chart(continent_data)
                
        else:
            # 특정 국가가 선택된 경우
            st.write(f"**'{selected_country}' 국가의 상세 데이터**")
            
            # 선택된 국가의 데이터만 필터링
            country_df = df[df['국가'] == selected_country].copy()
            
            # 1) 핵심 지표 표시
            latest_country_data = country_df[country_df['날짜'] == latest_date].iloc[0]
            
            col1, col2 = st.columns(2)
            col1.metric(
                label=f"총 누적 사망자 ({selected_country})",
                value=f"{latest_country_data['누적_사망자']:,}", # (천단위 콤마)
                delta=f"{latest_country_data['신규_사망자']:,} (최신)", # (신규 사망자)
                delta_color="inverse" # 숫자가 높을수록 나쁜 의미
            )
            col2.metric(
                label=f"대륙",
                value=latest_country_data['대륙']
            )
            
            # 2) 해당 국가의 차트 표시
            col1, col2 = st.columns(2)
            with col1:
                st.write("**누적 사망자 추이**")
                country_cum_trend = country_df.set_index('날짜')['누적_사망자']
                st.line_chart(country_cum_trend)
            with col2:
                st.write("**일별 신규 사망자**")
                country_new_trend = country_df.set_index('날짜')['신규_사망자']
                st.bar_chart(country_new_trend)

        st.markdown("---")
        
        # 6. 데이터 테이블
        st.subheader('🔢 최신 데이터 테이블 (정렬 가능)')
        st.write("칼럼 제목을 클릭하여 데이터를 정렬할 수 있습니다.")
        
        # latest_data에서 필요한 칼럼만 선택하여 표시
        display_columns = ['국가', '대륙', '누적_사망자', '신규_사망자', '위도', '경도']
        st.dataframe(latest_data[display_columns].set_index('국가'))

        # 7. 데이터 원본 표시 
        with st.expander("로드된 전체 원본 데이터 보기"):
            st.dataframe(df)

    else:
        st.warning("데이터 로드에 실패했습니다. 코드의 파일 경로를 확인해주세요.")
with tab3:
    st.header("백신 접종 현황")
    # 데이터 조회
    with st.sidebar:
        st.header("백신 접종 현황")
        st.selectbox("Input for Tab 3", ["A", "B"])
        st.select_slider("Input for Tab 3", [10, 20])

    df = pd.read_csv("COV_VAC_2021_2023_latlon.csv")

    col1, col2, col3 = st.columns(3)
    col1.metric("Temperature", "70 °F", "1.2 °F")
    col2.metric("Wind", "9 mph", "-8%")
    col3.metric("Humidity", "86%", "4%")

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
            map_style=None,
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