import websocket,json,sys,os,requests
from datetime import datetime,date

pair ='maticusdt'
interval = '1m'

capital = 5000
dca_bo=25
dca_so=50
dca_mstc = 10
dca_os = 1.5
dca_tp = 0.5
dca_sos = 0.5
dca_ss = 1.15

dca_so_count=0
dca_last_so = 0
dca_current_so=0


bot_total_volume = 0
bot_total_coins = 0
bot_avg_price = 0

last_bought_price = 0
next_so_buy_price = 0
sell_price = 0


def on_message(ws, message):
    data = json.loads(message)
    current_price = float(data['k']['c'])
    handle_trades(current_price)

def handle_trades(current_price):
    global capital,bot_total_volume,bot_total_coins,dca_bo,dca_so,dca_mstc,dca_os,dca_tp,dca_sos,dca_ss,last_bought_price,dca_current_so,dca_so_count,dca_last_so,next_so_buy_price,bot_avg_price,sell_price
    if bot_total_volume==0:
        buy_amount = dca_bo / float(current_price)
        bot_avg_price = current_price
        bot_total_coins += buy_amount
        next_so_buy_price = current_price - (current_price / 100 * dca_sos)
        sell_price = current_price + (current_price / 100 * dca_tp)
        bot_total_volume = bot_total_volume + (buy_amount * current_price)
        capital = capital - dca_bo
        print (f"we are buying {buy_amount} of {pair}")
        print (f"we now have {bot_total_coins} of {pair}")
        print (f"we will buy more at {next_so_buy_price}")
        print (f"we will sell  at {sell_price}")
        print (f"total volume is {bot_total_volume}")
        print (f"total available capital is {capital}")
        print (f"current usd total {capital + bot_total_volume}")
    else:
        #current_price=next_so_buy_price
        if current_price <=next_so_buy_price:
            if dca_current_so <dca_mstc:
                if dca_current_so ==0:
                    dca_current_so +=1
                    buy_amount = dca_so / float(current_price)
                    capital = capital - dca_so
                    dca_last_so = dca_so
                    bot_total_coins += buy_amount
                    next_so_buy_price = current_price - (current_price / 100 * dca_sos)
                    bot_total_volume = bot_total_volume + (buy_amount * current_price)

                    bot_avg_price = bot_total_volume / bot_total_coins

                    sell_price = bot_avg_price + (bot_avg_price / 100 * dca_tp)

                    dca_so_count = dca_so_count + 1
                    print (f"we are buying {buy_amount} of {pair}")
                    print (f"we now have {bot_total_coins} of {pair}")
                    print (f"we will buy more at {next_so_buy_price}")
                    print (f"avg_price is {bot_avg_price}")
                    print (f"we will sell  at {sell_price}")
                    print (f"total volume is {bot_total_volume}")
                    print (f"total available capital is {capital}")
                    print (f"current usd total {capital + bot_total_volume}")
                    print (f"number of so {dca_current_so}")
                    #sys.exit()
                else:
                    dca_current_so +=1
                    dca_last_so = dca_last_so * dca_os
                    capital = capital - dca_last_so
                    buy_amount = dca_last_so / float(current_price)
                    bot_total_coins += buy_amount
                    next_so_buy_price = current_price - (current_price / 100 * dca_sos)
                    bot_total_volume = bot_total_volume + (buy_amount * current_price)

                    bot_avg_price = bot_total_volume / bot_total_coins
                    sell_price = bot_avg_price + (bot_avg_price / 100 * dca_tp)

                    dca_so_count = dca_so_count + 1
                    print (f"we are buying {buy_amount} of {pair}")
                    print (f"we now have {bot_total_coins} of {pair}")
                    print (f"we will buy more at {next_so_buy_price}")
                    print (f"avg_price is {bot_avg_price}")
                    print (f"we will sell  at {sell_price}")
                    print (f"total volume is {bot_total_volume}")
                    print (f"total available capital is {capital}")
                    print (f"current usd total {capital + bot_total_volume}")
                    print (f"number of so {dca_current_so}")
        elif current_price >=sell_price:
            print (f"we will sell  now at {current_price}")
            sell_amount = bot_total_coins * current_price
            print (f"we sold {bot_total_coins} at {current_price}")
            print (f"total volume sold is {sell_amount}")
            capital = capital + sell_amount
            print (f"total capital is {capital}")

            dca_so_count=0
            dca_last_so = 0
            dca_current_so=0


            bot_total_volume = 0
            bot_total_coins = 0
            bot_avg_price = 0

            last_bought_price = 0
            next_so_buy_price = 0
            sell_price = 0



def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")


def get_historical_data(symbol, interval,limit,startTime):
    url = 'https://api.binance.com/api/v3/klines?symbol='+symbol+'&interval='+interval+'&limit='+str(limit)+'&startTime='+str(startTime)
    data = requests.get(url).json()

    for x in data:
        date = datetime.fromtimestamp(x[0]/1000)
        close_price = float(x[4])
        print (date,close_price)
        #return
        handle_trades(close_price)



#Simulate DCA with historical DATA starting from startTime...
#YOU can change the interval to 5m or 1h.
#This will simulate a much longer timeframe but is not accurate because we only look at the closing data of the candle.. 
startTime = date(2021, 5, 19).strftime("%s")+'000'
get_historical_data('MATICUSDT','1m',1500,startTime)


#LIVE SIMULATION!!!!
# socket = f'wss://stream.binance.com:9443/ws/{pair}@kline_{interval}'
# ws = websocket.WebSocketApp(socket,on_message = on_message,on_close=on_close)
#
# ws.run_forever()
