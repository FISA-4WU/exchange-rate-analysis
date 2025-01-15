import datetime
from bs4 import BeautifulSoup
import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import matplotlib
from dotenv import load_dotenv
import os



search_finish_date = st.date_input("여행 시작 날짜를 선택하세요", value=pd.Timestamp.today())
# search_finish_date = datetime(2021, 8, 12)
search_start_date = search_finish_date - datetime.timedelta(days=365 * 5)
currency = 'USD'

headers = {}
body = {
    'BAS_SDT': search_start_date.strftime('%Y%m%d'),
    'BAS_EDT': search_finish_date.strftime('%Y%m%d'),
    'BAS_DT': '',
    'CUR_Y': '',
    'CUR_M': '',
    'START_DATE_PRINT': '',
    'END_DATE_PRINT': '',
    'INQ_DIS_K': '',
    'INQ_DIS': currency,
    'a': '',
    'START_DATE_601_02': search_start_date.strftime('%Y.%m.%d'),
    'START_DATE_601_02Y': search_start_date.year,
    'START_DATE_601_02M': search_start_date.month,
    'START_DATE_601_02D': search_start_date.day,
    'END_DATE_601_02': search_finish_date.strftime('%Y.%m.%d'),
    'END_DATE_601_02Y': search_finish_date.year,
    'END_DATE_601_02M': search_finish_date.month,
    'END_DATE_601_02D': search_finish_date.day,
    'mm': '01',
}

response = requests.post(
    url='https://spib.wooribank.com/pib/jcc?withyou=CMCOM0185&__ID=c012349',
    headers=headers,
    data=body
)

soup = BeautifulSoup(response.text, 'html.parser')

trs = soup.select('#resultArea_601_02_01 > table > tbody > tr')

# 특정 단어("상" 또는 "하") 이전까지 텍스트를 슬라이싱하는 함수
def slice_text_before_keyword(td, keywords):
    text = td.get_text(strip=True)  # <td> 텍스트 가져오기
    for keyword in keywords:
        pos = text.find(keyword)
        if pos != -1:  # 키워드가 발견되면
            return text[:pos]  # 키워드 이전까지 슬라이싱
    return text  # 키워드가 없으면 원래 텍스트 반환

for tr in trs:
    tds = tr.find_all('td')
    date = datetime.datetime.strptime(tds[0].get_text(), '%Y.%m.%d')   # 첫 번째 <td>
    trading_base_rate = slice_text_before_keyword(tds[5], ['상', '하'])  # 여섯 번째 <td>

    print(date, trading_base_rate)