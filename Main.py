import BB_main
import requests
import webbrowser
import MockMain
import Portfolio
from io import BytesIO
from server import *


class Main:
    def on_portfolio_click(self):
        Portfolio.portfolio(self.window)

    def on_simulation_click(self):
        MockMain.MockInvestmentApp(self.window)

    def on_bollinger_click(self):
        BB_main.BBMain(self.window)
    

    def __init__(self):
        # 창 생성
        self.window = Tk()
        self.window.title("MENU")
        self.window.geometry("300x130")
        self.window.rowconfigure(4, weight=1)  # row 4의 크기를 조정 가능하도록 설정
        self.window.columnconfigure(0, weight=1)  # column 0의 크기를 조정 가능하도록 설정

        # 프레임 생성
        frame = Frame(self.window)
        frame.grid(column=0, row=0, sticky="nsew")
   
       # 뉴스 프레임 생성 (높이 100으로 변경)
        self.current_index = 0
        self.news_frame = Frame(self.window, width=330, height=30, bg="blue")
        self.news_frame.grid(column=0, row=5, sticky="ew")

        # 뉴스 정보 가져오기
        query = "경제"
        self.articles = self.get_naver_news(query)
        self.news_title = self.articles[self.current_index]["title"]

        # 라벨 배경색 변경 및 높이 설정
        self.news_label = Label(self.news_frame, bg="blue", fg="yellow")
        self.news_label.place(x=330, y=0)  # 라벨을 프레임 내에서 초기 위치로 설정
        self.move_label()

        # 뉴스 라벨 클릭 이벤트 바인딩
        self.news_label.bind("<Button-1>", lambda e: webbrowser.open(self.articles[self.current_index - 1]["link"]))
        # 뉴스 표시
        self.display_news()
         # 버튼 생성 및 배치
        portfolio_button = Button(frame, text="포트폴리오",font=("Arial", 11), command=self.on_portfolio_click,height=3)
        portfolio_button.grid(column=0, row=0, padx=11, pady=15)

        simulation_button = Button(frame, text="모의 투자",font=("Arial", 11), command=self.on_simulation_click,height=3)
        simulation_button.grid(column=1, row=0, padx=13, pady=15)

        bollinger_button = Button(frame, text="차트 분석",font=("Arial", 11), command=self.on_bollinger_click,height=3)
        bollinger_button.grid(column=2, row=0, padx=13, pady=15)
        self.window.mainloop()

    def move_label(self):
        current_position = self.news_label.winfo_x()
        if current_position <= -self.news_label.winfo_reqwidth():
            self.current_index = (self.current_index + 1) % len(self.articles)
            self.news_title = self.articles[self.current_index]["title"]
            self.news_label.config(text=self.news_title)
            current_position = self.news_frame.winfo_width()
            self.news_frame.after(0, lambda: self.display_news())

        self.news_label.place(x=current_position - 1, y=0)
        self.news_label.after(20, self.move_label)

    
    def get_naver_news(self, query):
        client = Client()
        url = "https://openapi.naver.com/v1/search/news.json"
        headers = {
            "X-Naver-Client-Id": client.get_Naver_Client_ID(),
            "X-Naver-Client-Secret": client.get_Naver_Client_SECRET()
        }

        params = {
            "query": query,
            "display": 10
        }
        response = requests.get(url, headers=headers, params=params)
        news_data = response.json()

        if news_data:
            return news_data["items"]
        else:
            print("Error fetching news data")
            return []
        
    def display_news(self):
        news_title = self.articles[self.current_index]["title"]
        self.news_label.config(text=news_title)
        self.current_index = (self.current_index + 1) % len(self.articles)
     

Main()