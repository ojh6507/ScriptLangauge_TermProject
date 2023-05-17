from server import *
from bollinger_bands import *
from stock_search import*

matplotlib.use("TkAgg")
yf.pdr_override()
supported_intervals = ["60m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
ticker = ''
class BBMain:
    def display_companies(self, companies, start):
        for i in range(5):
            if start + i < len(companies):
                company_name = list(companies.keys())[start + i]
                self.results_listbox.insert(END, company_name)
            else:
                break

    def next_page(self):
        self.start_index += 5
        self.results_listbox.delete(0, END)
        self.display_companies(self.results, self.start_index)

    def prev_page(self):
        if self.start_index > 0:
            self.start_index -= 5
            self.results_listbox.delete(0, END)
            self.display_companies(self.results, self.start_index)

    def show_search_results(self):
        global ticker
        if self.results:
            if self.market == 'Nasdaq':
                self.search_results_window = Toplevel(self.root)
                self.search_results_window.title("검색 결과")
                self.results_listbox = Listbox(self.search_results_window, selectmode=SINGLE)
                
                for result in self.results:
                    self.results_listbox.insert(END, result)

                self.results_listbox.pack(padx=20, pady=20)
                select_button = Button(self.search_results_window, text="선택", command = self.on_result_select)
                select_button.pack(padx=20, pady=20)

            elif self.market == 'kor':
                if isinstance(self.results,list):
                    ticker = self.results[0]
                    self.update_chart_thread()
                elif isinstance(self.results, dict):
                    self.search_results_window = Toplevel(self.root)
                    self.search_results_window.title("검색 결과")
                    self.results_listbox = Listbox(self.search_results_window, selectmode=SINGLE)

                    self.start_index = 0
                    self.display_companies(self.results, self.start_index)

                    self.results_listbox.pack(padx=20, pady=20)

                    prev_button = Button(self.search_results_window, text="Prev", command=self.prev_page)
                    prev_button.pack(side=LEFT)

                    next_button = Button(self.search_results_window, text="Next", command=self.next_page)
                    next_button.pack(side=RIGHT)

                    select_button = Button(self.search_results_window, text="선택", command=self.on_result_select)
                    select_button.pack(padx=20, pady=20)
        else:
            self.action_label.config(text="검색 결과를 찾을 수 없습니다.")
    
    def on_result_select(self):
        global ticker
        self.selected_index = self.results_listbox.curselection()
        if self.selected_index:
            if isinstance(self.results, dict):
                key = self.results_listbox.get(self.selected_index[0])
                ticker = self.results[key]
                print('ticker: ',ticker)
            else:
                ticker = self.results[self.selected_index[0]]
            self.search_results_window.destroy()
            self.update_chart_thread()
    
    def search_stock(self):
        company_name = self.company_entry.get()
        self.market, self.results = search_tickers_by_name(company_name)
        if self.results:
            self.show_search_results()
        else:
            self.action_label.config(text="검색 결과를 찾을 수 없습니다.")


    def update_chart_thread(self):
        update_thread = threading.Thread(target=self.update_chart)
        update_thread.start()

    def show_loading_screen(self):
        loading_screen = Toplevel(self.root)
        loading_screen.title("Loading...")
        loading_label = Label(loading_screen, text="데이터를 로드하는 중입니다. 잠시 기다려 주세요...")
        loading_label.pack(padx=20, pady=20)

        progressbar = ttk.Progressbar(loading_screen, mode="indeterminate")
        progressbar.pack(padx=20, pady=20)
        progressbar.start()
        progressbar.update()

        loading_screen.lift()
        self.root.attributes("-disabled", True)
        self.root.update()  # Change this line

        return loading_screen, progressbar

    def hide_loading_screen(self,loading_screen, progressbar):
        progressbar.stop()
        self.root.attributes("-disabled", False)
        loading_screen.destroy()


    def get_default_window(self, interval):
        if interval in ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"]:
            return 20
        elif interval in ["1d", "5d"]:
            return 20
        elif interval == "1wk":
            return 4
        elif interval in ["1mo", "3mo"]:
            return 3
        else:
            return 20


    def update_chart(self):
        global ticker
        if ticker!='':
            loading_screen, progressbar = self.show_loading_screen()
            self.root.update()

            interval = self.interval_var.get()
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            window = self.window_var.get()

            stock_data = download_stock_data(ticker, start_date, end_date, interval)
            stock_data = calculate_bollinger_bands(stock_data, window)
                # Get company name
            stock_ticker = yf.Ticker(ticker)
            company_info = stock_ticker.info
            company_name = company_info.get('shortName', ticker)

            self.fig.clf()
            if not stock_data.empty:
                action = analyze_bollinger_bands(stock_data)
                self.action_label.config(text=f"현재 주가에 대한 추천: {action}")

                self.fig.clf()
                ax = self.fig.add_subplot(111)
                ax.plot(stock_data.index, stock_data['Close'], label='Close', color='blue')
                ax.plot(stock_data.index, stock_data['Moving Average'], label='Moving Average', color='red')
                ax.plot(stock_data.index, stock_data['Upper Band'], label='Upper Band', color='green')
                ax.plot(stock_data.index, stock_data['Lower Band'], label='Lower Band', color='orange')
                ax.fill_between(stock_data.index, stock_data['Lower Band'], stock_data['Upper Band'], color='gray', alpha=0.2)
                ax.set_title(f"{company_name} Bollinger Bands")
                ax.set_xlabel("Date")
                ax.set_ylabel("Price")
                ax.legend(loc="best")
            else:
                 self.action_label.config(text="주가 데이터를 찾을 수 없습니다.")
            self.canvas.draw()
            self.hide_loading_screen(loading_screen, progressbar)

    def update_window(self, *args):
        interget = self.interval_var.get()
        default_window = self.get_default_window(interget)
        self.window_var.set(default_window)

    def __init__(self):
        self.root = Tk()
        self.root.title("Bollinger Bands Analyzer")

        self.interval_var = StringVar( self.root)
        self.interval_var.set("1d")  # default value
        self.interval_var.trace("w", self.update_window)


        
        self.interval_optionmenu = OptionMenu(self.root, self.interval_var, *supported_intervals)
        self.window_var = IntVar(self.root)
        self.window_var.set(20)  # default value

        self.company_label = Label(self.root, text="회사 이름:")
        self.company_label.pack()
        self.company_entry = Entry(self.root)
        self.company_entry.pack()

        self.search_button = Button(self.root, text="검색", command=self.search_stock)
        self.search_button.pack()

        self.window_label = Label(self.root, text="이동 평균 기간 선택:")
        self.window_label.pack()
        self.interval_label = Label(self.root, text="주기 선택:")
        self.interval_label.pack()
        self.interval_optionmenu.pack()
      
        window_spinbox = Spinbox(self.root, from_=1, to=100, textvariable=self.window_var)
      
        window_spinbox.pack()

        update_button = Button(self.root, text="차트 업데이트", command=self.update_chart_thread)
        update_button.pack()

        self.action_label = Label(self.root, text="현재 주가에 대한 추천:")
        self.action_label.pack()

        self.fig = plt.figure(figsize=(12, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack()

        self.root.protocol("WM_DELETE_WINDOW", lambda: self.on_window_close(self.root))
        self.update_chart()
        self.root.mainloop()
        # 창 종료 이벤트 처리 함수
    def on_window_close(self, root):
        global ticker
        ticker =''
        root.quit()
        root.destroy()
