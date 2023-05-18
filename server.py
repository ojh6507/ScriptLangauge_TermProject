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
        self.naver_CLIENT_ID = 'x9NjT2FRk8MvnFKl2u2f'
        self.naver_CLIENT_SECRET = 'bE4jGzFWfd'
    
    def get_Naver_Client_ID(self):
        return self.naver_CLIENT_ID
    
    def get_Naver_Client_SECRET(self):
        return self.naver_CLIENT_SECRET

    