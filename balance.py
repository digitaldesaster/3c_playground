#!/usr/bin/env python
# -*- coding: utf-8 -*-
from py3cw.request import Py3CW

#playin around with 3commas api
#this scripts assumes that you are trading USDT pairs.

#put in you key and secret from 3commas
key = ''
secret = ''

p3cw = Py3CW(
    key=key,
    secret=secret,
    request_options={
        'request_timeout': 10,
        'nr_of_retries': 1,
        'retry_status_codes': [502]
    }
)


def getAccounts():
    error, data = p3cw.request(
        entity='accounts',
        action=''
    )
    accounts=[]
    for account in data:
        account_id = account['id']
        exchange_name = account['name']
        accounts.append({'id':account_id,'exchange_name':exchange_name})
    return accounts

#gets Data about all Coins in the specific account
def getCoinBalance(account_id,get_coin=''):
    error, data = p3cw.request(
        entity='accounts',
        action='pie_chart_data',
        action_id=str(account_id)
    )

    #print (error)
    coins_in_balance = []
    for coin in data:
        if get_coin !='' and (coin['code']) ==get_coin:
            return coin['usd_value']
        coin_symbol = coin['code']
        usd_value = coin['usd_value']
        amount = coin['amount']
        coinmarketcapid = coin['coinmarketcapid']
        coins_in_balance.append({'coin': coin_symbol,'usd_value':usd_value})

    return coins_in_balance

def getDeals(account_id,total_volume_only=False):
    error, data  = p3cw.request(
    entity='deals',
    action='',
    payload={
        "scope": 'active',
        "account_id" : account_id
    }
)
    coins_in_deals = []
    total_volume = 0
    total_so=0
    total_usd_profit = 0
    for coin in data:
        #print (account_id)
        #for parameter in coin:
        #    print (parameter)

        coin_symbol = coin['to_currency']
        #print (coin['pair'])
        bought_volume = coin['bought_volume']
        total_volume = total_volume + round(float(bought_volume),2)
        active_so = coin['completed_safety_orders_count']
        total_so = total_so + active_so
        current_price = coin['current_price']
        take_profit_price = coin['take_profit_price']
        actual_usd_profit = coin['actual_usd_profit']
        total_usd_profit = total_usd_profit + round(float(actual_usd_profit),2)
        #print (coin_symbol,bought_volume)
        coins_in_deals.append({'coin': coin_symbol,'bought_volume':bought_volume,'active_so':active_so,'current_price':current_price,'take_profit_price':take_profit_price,'actual_usd_profit':actual_usd_profit})
        #print (coin['current_price'])
        #print (coin['take_profit_price'])
        #print (coin['bought_amount'])
    if total_volume_only==True:
        return total_volume
    else:
        return {'coins_in_deals' : coins_in_deals,'total_usd_profit' : round(total_usd_profit,2),'total_so':total_so
        }

def getBots(account_id,so=0):
    error, data = p3cw.request(
        entity='bots',
        action='',
        payload={
            "scope": 'enabled',
            "account_id" : account_id
        }
        )
    coins_in_bots = []

    total_volume = 0

    avg_safety_order = 0

    active_bots = len(data)

    for coin in data:
        i=0

        total_volume_of_coin = float(coin['base_order_volume'])
        safety_order_volume = float(coin['safety_order_volume'])
        safety_order_volume_scale = float(coin['martingale_volume_coefficient'])

        if so!=0:
            max_safety_orders = so
        else:
            max_safety_orders = coin['max_safety_orders']

        while i < max_safety_orders:
            total_volume_of_coin = total_volume_of_coin + safety_order_volume
            safety_order_volume = safety_order_volume * safety_order_volume_scale
            i=i+1

        if avg_safety_order ==0:
            avg_safety_order = max_safety_orders
        else:
            avg_safety_order = (avg_safety_order + max_safety_orders) / 2

        if coin['type']!='Bot::SingleBot':
            max_active_deals = float(coin['max_active_deals'])
            total_volume_of_coin = total_volume_of_coin * max_active_deals

        total_volume = total_volume + total_volume_of_coin

    return round(total_volume,2),round(avg_safety_order,2),active_bots


        #print (coin['account_id'])
        #coin_symbol = coin['to_currency']
            #print (coin['pair'])
            #bought_volume = coin['bought_volume']
            #print (coin_symbol,bought_volume)
            #coins_in_deals.append({'coin': coin_symbol,'bought_volume':bought_volume})
            #print (coin['current_price'])
            #print (coin['take_profit_price'])
            #print (coin['bought_amount'])
    #print (coins_in_deals)


def checkAccount(acc_id):

    #get all accounts and ids
    accounts =  getAccounts()

    #take the first account
    account_id = accounts[acc_id]['id']

    #usdt available on exchange now!
    get_coin ='BUSD'
    usdt_value = float(getCoinBalance(account_id,get_coin))
    #print ('Balance of ' + get_coin +': '+ str(usdt_value))

    #usdt available on exchange now!
    get_coin ='USDT'
    usdt_value = usdt_value + float(getCoinBalance(account_id,get_coin))

    #print ('Balance of ' + get_coin +': '+ str(round(usdt_value,2)))

    #gets balance of all coins in usd
    #all_coins = getCoinBalance(account_id)
    #print (all_coins)

    #total_volume of all deals at the moment
    usdt_in_deals = round(getDeals(account_id,True),2)
    #print ('USDT stuck in deals: ' + str(total_volume))

    #sum of available usdt and volume stuck in deals..
    total_capital = round (usdt_value + usdt_in_deals,2)
    #print ('Total current balance: ' + str(total_capital))

    #available USDT in percent from total_capital (coins on exchange excluded)
    liquidity = round(100 - (100/total_capital *usdt_in_deals),2)
    #print ('Liquidity in % :' + str(liquidity)

    #calculated avg_safety_order
    total_bot_volume,avg_safety_order,active_bots = getBots(account_id)
    risk_factor = round(100/total_capital*total_bot_volume,2)

    #print ('Total Bot Volume: '+ str(total_bot_volume))

    #print ('Riskfactor with '+ str(avg_safety_order) + ' SO: ' + str(risk_factor) + '%')

    #print ('Active Bots: ' + str(active_bots))

    return {'usdt_balance' : usdt_value,'usdt_in_deals' : usdt_in_deals,'total_capital' : total_capital,'liquidity': liquidity,'total_bot_volume':total_bot_volume,'avg_safety_order':avg_safety_order,'active_bots':active_bots,'risk_factor':risk_factor}

bot_status = checkAccount(1)

print (bot_status)


accounts =  getAccounts()
account_id = accounts[1]['id']

print (getDeals(account_id))



#
# #asuming avg_safety_order: 20
# total_bot_volume,avg_safety_order = getBots(account_id,20)
# risk_factor = round(100/total_capital*total_bot_volume,2)
# print ('Riskfactor with '+ str(avg_safety_order) + ' SO: ' + str(risk_factor) + '%')
#
# #asuming avg_safety_order: 30
# total_bot_volume,avg_safety_order = getBots(account_id,30)
# risk_factor = round(100/total_capital*total_bot_volume,2)
# print ('Riskfactor with '+ str(avg_safety_order) + ' SO: ' + str(risk_factor) + '%')
