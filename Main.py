
import tkinter as tk
from tkinter import ttk
import requests
import webbrowser
import MockMain
from io import BytesIO
from server import Client 
class Main:
    def on_portfolio_click(self):
        print("포트폴리오 메뉴를 선택했습니다.")

    def on_simulation_click(self):
        print("모의 투자 메뉴를 선택했습니다.")
      

    def on_bollinger_click(self):
        print("볼린저 밴드 분석 메뉴를 선택했습니다.")

    

    def __init__(self):
        # 창 생성
        window = tk.Tk()
        window.title("MENU")
        window.geometry("300x130")
        window.rowconfigure(4, weight=1)  # row 4의 크기를 조정 가능하도록 설정
        window.columnconfigure(0, weight=1)  # column 0의 크기를 조정 가능하도록 설정

        # 프레임 생성
        frame = ttk.Frame(window)
        frame.grid(column=0, row=0, sticky="nsew")
      
        portfolio_button = tk.Button(frame, text="포트폴리오", command=self.on_portfolio_click,height=3)
        portfolio_button.grid(column=0, row=0, padx=10, pady=15)

        simulation_button = tk.Button(frame, text="모의 투자", command=self.on_simulation_click,height=3)
        simulation_button.grid(column=1, row=0, padx=10, pady=15)

        bollinger_button = tk.Button(frame, text="볼린저 밴드 분석", command=self.on_bollinger_click,height=3)
        bollinger_button.grid(column=2, row=0, padx=10, pady=15)
        window.mainloop()

    
   

Main()