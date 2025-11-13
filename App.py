import streamlit as st

st.title("코로나 대시보드")

tab1, tab2, tab3 = st.tabs(
    ["확진자 현황", "사망자 현황", "백신 접종 현황"]
)

with tab1:
    st.header("확진자 현황")
with tab2:
    st.header("사망자 현황")
with tab3:
    st.header("백신 접종 현황")