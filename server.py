import requests
import matplotlib
import threading
import numpy as np
import pandas as pd
from tkinter import *
import yfinance as yf
from tkinter import ttk
from bs4 import BeautifulSoup
import tkinter.messagebox as messagebox
import matplotlib.pyplot as plt

from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pandas import DataFrame
from pandas_datareader import data as pdr
from datetime import datetime, timedelta
import urllib.parse


#naver Client
class Client:
    def __init__(self):

        '''네이버 API'''
        self.naver_CLIENT_ID = 'x9NjT2FRk8MvnFKl2u2f'
        self.naver_CLIENT_SECRET = 'bE4jGzFWfd'
        
        
        '''한국투자증권 API'''
        self.koreaInvest_ID ='PSi8y6hvV0M0YN5DWPR6xnduteM5Rp6GtagL'
        self.koreaInvest_SECRET ='dXHpdzAF7arfSQ8qNkQF8Olc1Lf0H9j1nvcNm5PQCxOxwc1iXwjtgH5DPntP/KWsZGzOw+WDYlfRHd01Rfdbz5pZ1xiCZcgxBnPlMag3QL/zsVC2gpewBjhjYFaPwdosbHi32jyCt2lHpz35fvOoR1TVaqIed234mXB4VA4w4eAGVYT3GMI='
        #계좌번호 앞 8자리
        self.CANO= "73571774"
        #계좌번호 뒤 2자리
        self.ACNT_PRDT_CD= "01"
        #실전투자
        self.URL_BASE= "https://openapi.koreainvestment.com:9443"
        #모의투자
        # URL_BASE: "https://openapivts.koreainvestment.com:29443"

    def get_Naver_Client_ID(self):
        return self.naver_CLIENT_ID
    def get_Naver_Client_SECRET(self):
        return self.naver_CLIENT_SECRET
    
    def get_KoreaInvest_ID(self):
        return self.koreaInvest_ID
    def get_KoreaInvest_SECRET(self):
        return self.koreaInvest_SECRET
    
    def get_CANO(self):
        return self.CANO
    def get_ACNT_PRDT_CD(self):
        return self.ACNT_PRDT_CD
    def get_URL_Base(self):
        return self.URL_BASE
    

    