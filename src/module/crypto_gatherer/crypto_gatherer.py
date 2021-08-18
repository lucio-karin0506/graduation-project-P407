import investpy
from datetime import datetime

def crypto_gatherer(coin:str, start_date:str, end_date:str):
    
    crypto_dict_list = investpy.get_cryptos_dict()
    for crypto_dict in crypto_dict_list:
        if crypto_dict['symbol'].lower() == coin.lower():
            coin = crypto_dict['name']
            break
    start_date = datetime.strftime(datetime.strptime(start_date, '%Y-%m-%d'), '%d/%m/%Y')
    end_date = datetime.strftime(datetime.strptime(end_date, '%Y-%m-%d'), '%d/%m/%Y')
    data = investpy.get_crypto_historical_data(crypto=coin,
                                               from_date=start_date,
                                               to_date=end_date,
                                                order='ascending')
    data.columns = [name.lower() for name in list(data.columns)]
    return data

if __name__ == '__main__':
    # df = crypto_gatherer('BTC', '2020-01-01', '2020-12-31')
    # print(df)
    able_list = []
    unable_list = []
    # for name in investpy.get_cryptos_list():
    #     try:
    #         crypto_gatherer(name, '2021-01-01', '2021-01-31')
    #         able_list.append(name)
    #     except:
    #         unable_list.append(name)
    print(investpy.get_cryptos_list())
    # print('a')
   