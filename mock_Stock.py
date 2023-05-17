class STOCK:
    def __init__(self, name, ticker, price, amount):
        self.name = name
        self.ticker = ticker
        self.per_price = price
        self.amount = amount
    def getName(self):
        return self.name
    def getTicker(self):
        return self.ticker
    def get_per_Price(self):
        return self.per_price
    def get_total_Price(self):
        return self.per_price * self.amount
    def getAmount(self):
        return self.amount
    def update_amount(self, amount):
        self.amount += amount
    def update_Sell_amount(self, amount):
        self.amount -= amount
