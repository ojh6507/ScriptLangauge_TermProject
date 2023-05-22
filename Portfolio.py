from server import *



class portfolio:
    def __init__(self,root):
        self.window = Toplevel(root)
        self.window.title('포트폴리오')
        self.window.geometry('400x300')
          # 포트폴리오 Frame
        self.portfolio_listbox = Listbox(self.window,width=40)
        self.portfolio_listbox.pack(padx=20, pady=20)
        self.add_button = Button(self.window, text="추가", command=self.add_stock)
        self.add_button.place(x=250, y=200, width=30, height=30)
      
        self.sav_button = Button(self.window, text="저장", command=self.save_stocks)
        self.sav_button.place(x=290, y=200, width=30, height=30)
        self.sav_button = Button(self.window, text="불러오기", command=self.load_stocks)
        self.sav_button.place(x=330, y=200, width=50, height=30)

        self.window.mainloop()
    def add_stock(self):
        sub_window = Toplevel(self.window)
        stock_name_label = Label(sub_window,text = '종목명: ')
        stock_name_label.pack(side='left')
        stock_name_blank = Entry(sub_window)
        stock_name_blank.pack()

        stock_count_label = Label(sub_window,text = '수량: ')
        stock_count_label.pack(side='left')
        stock_count_blank = Entry(sub_window)
        stock_count_blank.pack()
        
        sub_window.mainloop()
        pass
    def save_stocks(self):
        pass
    def load_stocks(self):
        pass


if __name__ == '__main__':
    root = Tk()
    portfolio(root)