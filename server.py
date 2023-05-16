import numpy as np
import yfinance as yf
from bs4 import BeautifulSoup
import requests

import threading
from tkinter import *
from tkinter import Toplevel, ttk
import tkinter.messagebox as messagebox

from datetime import datetime, timedelta

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from pandas import DataFrame
from pandas_datareader import data as pdr
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

    