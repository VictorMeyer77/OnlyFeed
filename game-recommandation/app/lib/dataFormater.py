from currency_converter import CurrencyConverter
import numpy as np

def cleanGameData(dictData):

    dictData["price"] = convertPrices(dictData["price"], dictData["currency"], "EUR")
    dictData["release_date"] = datesToTimestamp(dictData["release_date"])
    dictData["genres"] = getFirstListItem(dictData["genres"])
    dictData["genres"] = hashColumn(dictData["genres"])
    dictData["publishers"] = hashColumn(dictData["publishers"])
    dictData["developers"] = getFirstListItem(dictData["developers"])
    dictData["developers"] = hashColumn(dictData["developers"])

    del dictData["currency"]

    return np.array(list(dictData.values())).astype("float64")

def hashColumn(col):

    hashs = []

    for ele in col:
        hashs.append(abs(hash(ele)) % (10 ** 8))

    return hashs

def getFirstListItem(column):

    firsts = []

    for ele in column:
        firsts.append(ele.split(",")[0])

    return firsts

def datesToTimestamp(dateList):

    timestamps = []

    for date in dateList:
        timestamps.append(date.timestamp())

    return timestamps

def convertPrices(prices, currencies, currencyTarget):

    conertPrices = []
    converter = CurrencyConverter()

    for i in range(len(prices)):

        if currencies[i] not in converter.currencies:
            print("INFO: {} non pris en charge.".format(currencies[i]))

        conertPrices.append(converter.convert(prices[i], currencies[i], currencyTarget))

    return conertPrices
