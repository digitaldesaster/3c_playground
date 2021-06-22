import websocket,json,sys,os,requests
from datetime import datetime,date
from time import sleep

pair ='matiusdt'
interval = '1m'

start_capital=5000
capital = start_capital
dca_base_order=25
dca_safety_order=50
dca_max_safety_orders = 10
dca_safety_order_volume_scale = 1.5
dca_target_profit = 0.5
dca_deviation_to_open_safety_order = 0.5
dca_safety_order_step_scale = 1.15

dca_trading_fee = 0.075


def reset_status():
    global capital,bot_total_volume,bot_total_coins,dca_base_order,dca_safety_order,dca_max_safety_orders,dca_safety_order_volume_scale,dca_target_profit,dca_deviation_to_open_safety_order,dca_safety_order_step_scale,last_bought_price,dca_current_safety_order,dca_last_safety_order,next_so_buy_price,bot_avg_price,sell_price,dca_trading_fee

    dca_last_safety_order = 0
    dca_current_safety_order=0

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

def current_status(buy_amount):
    global capital,bot_total_volume,bot_total_coins,dca_base_order,dca_safety_order,dca_max_safety_orders,dca_safety_order_volume_scale,dca_target_profit,dca_deviation_to_open_safety_order,dca_safety_order_step_scale,last_bought_price,dca_current_safety_order,dca_last_safety_order,next_so_buy_price,bot_avg_price,sell_price,dca_trading_fee
    print (f"we are buying {buy_amount} of {pair}")
    print (f"we now have {bot_total_coins} of {pair}")
    print (f"we will buy more at {next_so_buy_price}")
    print (f"avg_price is {bot_avg_price}")
    print (f"we will sell  at {sell_price}")
    print (f"total volume is {bot_total_volume}")
    print (f"total available capital is {capital}")
    print (f"current usd total {capital + bot_total_volume}")
    if dca_current_safety_order !=0:
        print (f"number of so {dca_current_safety_order}")

def handle_trades(current_price):
    global capital,bot_total_volume,bot_total_coins,dca_base_order,dca_safety_order,dca_max_safety_orders,dca_safety_order_volume_scale,dca_target_profit,dca_deviation_to_open_safety_order,dca_safety_order_step_scale,last_bought_price,dca_current_safety_order,dca_last_safety_order,next_so_buy_price,bot_avg_price,sell_price,dca_trading_fee
    if bot_total_volume==0:
        buy_amount = dca_base_order / float(current_price)
        bot_avg_price = current_price
        bot_total_coins += buy_amount
        next_so_buy_price = current_price - (current_price / 100 * dca_deviation_to_open_safety_order)
        sell_price = current_price + (current_price / 100 * dca_target_profit)
        bot_total_volume = bot_total_volume + (buy_amount * current_price)
        capital = capital - dca_base_order
        capital = capital - (dca_base_order/100*dca_trading_fee)
        current_status(buy_amount)
    else:
        #current_price=next_so_buy_price
        if current_price <=next_so_buy_price:
            if dca_current_safety_order <dca_max_safety_orders:
                if dca_current_safety_order ==0:
                    dca_last_safety_order = dca_safety_order
                else:
                    dca_last_safety_order = dca_last_safety_order * dca_safety_order_volume_scale

                capital = capital - dca_last_safety_order
                capital = capital - (dca_last_safety_order/100*dca_trading_fee)
                buy_amount = dca_last_safety_order / float(current_price)


                dca_current_safety_order +=1
                bot_total_coins += buy_amount
                next_so_buy_price = current_price - (current_price / 100 * dca_deviation_to_open_safety_order)
                bot_total_volume = bot_total_volume + (buy_amount * current_price)
                bot_avg_price = bot_total_volume / bot_total_coins
                sell_price = bot_avg_price + (bot_avg_price / 100 * dca_target_profit)

                current_status(buy_amount)



        elif current_price >=sell_price:
            print (f"we will sell  now at {current_price}")
            sell_amount = bot_total_coins * current_price
            print (f"we sold {bot_total_coins} at {current_price}")
            print (f"total volume sold is {sell_amount}")
            capital = capital + sell_amount
            print (f"total capital is {capital}")
            reset_status()





def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")


def get_historical_data(symbol, interval,limit,startTime=0,storeLocal=False):
    global pair
    pair = symbol
    if startTime !=0:
        url = 'https://api.binance.com/api/v3/klines?symbol='+symbol+'&interval='+interval+'&limit='+str(limit)+'&startTime='+str(startTime)
    else:
        url = 'https://api.binance.com/api/v3/klines?symbol='+symbol+'&interval='+interval+'&limit='+str(limit)
    data = requests.get(url).json()

    if storeLocal:
        file_name=symbol + ".txt"
        f = open(file_name, "a")

    for x in data:
        date = datetime.fromtimestamp(x[0]/1000)
        close_price = float(x[4])
        #print (x[0],date,close_price)
        #return
        if storeLocal:
            f.write(str(date) + ';' + str(close_price) + '\n')

        #this function handles all the trades..
        handle_trades(close_price)


    if storeLocal:
        f.close()

    #next dataset
    next_time = int(x[0]) + 60000

    return next_time


#This function processes the local data
def processLocalData(symbol):
    reset_status()
    global bot_total_volume,buy_amount
    file_name=symbol + ".txt"
    f = open(file_name, "r")
    content = f.readlines()
    for line in content:
        data = line.strip().split(';')
        #print (data[0])
        last_price = float(data[1])
        handle_trades(last_price)
    bot_total_volume = bot_total_coins * last_price
    print (f"last_price is {last_price}")
    print (f"total volume is {bot_total_volume}")
    print (f"total available capital is {capital}")
    print (f"total capital is {bot_total_volume + capital}")


#This function downloads all 1m data into a local file. e.g. MATICUSDT.txt
def downloadPriceData(symbol):
    startTime = date(2021, 6, 1).strftime("%s")+'000'
    endTime = datetime.now().strftime("%s")+'000'
    lastTime = startTime

    try:
        file_name=symbol + ".txt"
        os.remove(file_name)
    except:
        pass

    while int(endTime) > int(lastTime):
        lastTime = get_historical_data(symbol,'1m',1500,lastTime,True)
        sleep(1)


reset_status()

#This function downloads all 1m data into a local file. e.g. MATICUSDT.txt
#delete an existing file if you start this function again.. because it only appends data!!!!!!!!
#downloadPriceData('AAVEUSDT')
#downloadPriceData('DGBUSDT')
#downloadPriceData('TRXUSDT')
#downloadPriceData('VETUSDT')
#downloadPriceData('UNIUSDT')
#downloadPriceData('THETAUSDT')
#downloadPriceData('SOLUSDT')
#downloadPriceData('MATICUSDT')
#This function processes the local data
# dca_base_order=10
# dca_safety_order=20
# dca_safety_order_volume_scale = 1.5
# dca_max_safety_orders = 10
# dca_target_profit = 0.6
# dca_deviation_to_open_safety_order = 0.6
# dca_safety_order_step_scale = 1.15
# processLocalData('MATICUSDT')

#This function get the last 1500 datapoints (limit)...
#dca_deviation_to_open_safety_order = 0.6
get_historical_data('MATICUSDT','1m',1500)


#LIVE SIMULATION!!!!
# socket = f'wss://stream.binance.com:9443/ws/{pair}@kline_{interval}'
# ws = websocket.WebSocketApp(socket,on_message = on_message,on_close=on_close)
#
# ws.run_forever()
