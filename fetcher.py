#This file is where it will get the stock ticker symbol and return the current price

import yfinance as yf


def price_check(stock_symbol):

    #Get the ticket for the stock
    stock = yf.Ticker(stock_symbol)

    #Get the price
    price = stock.info["currentPrice"]

    return price
