from lib.postgresDao import PostgresDao
from datetime import datetime
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import normalize
from currency_converter import CurrencyConverter
import numpy as np
import matplotlib.pyplot as plt

class NearFavoriteGame:

    def __init__(self, postgresDao, nearestNeightboor, radius, priceCurrency="EUR"):

        self.postgresDao = postgresDao
        self.priceCurrency = priceCurrency

        sqlData = self.postgresDao.getGameDataset()
        dataset = self.cleanData(sqlData)
        self.network = self.clusterize(dataset[1:, :].T, nearestNeightboor, radius)

    def cleanData(self, sqlData):

        dictData = self.extractDataset(sqlData)
        dictData["price"] = self.convertPrices(dictData["price"], dictData["currency"], self.priceCurrency)
        dictData["release_date"] = self.datesToTimestamp(dictData["release_date"])
        dictData["genres"] = self.hashColumn(dictData["genres"])
        dictData["publishers"] = self.hashColumn(dictData["publishers"])
        dictData["developers"] = self.hashColumn(dictData["developers"])

        del dictData["currency"]

        return np.array(list(dictData.values())).astype("float64")

    @staticmethod
    def clusterize(dataset, nearestNeightboor, radius):

        network = NearestNeighbors(n_neighbors=nearestNeightboor, radius=radius)
        neightboors = network.fit(dataset)
        distances, indices = neightboors.kneighbors(dataset)
        print(distances)
        print(distances.shape)
        distances = np.sort(distances, axis=0)
        distances = distances[:, 1]
        plt.plot(distances)
        plt.show()


    @staticmethod
    def extractDataset(sqlResponse):

        dataset = {"id": [],
                   "release_date": [],
                   "genres": [],
                   "price": [],
                   "currency": [],
                   "age": [],
                   "windows": [],
                   "mac": [],
                   "linux": [],
                   "publishers": [],
                   "developers": [],
                   "graphic": [],
                   "gameplay": [],
                   "lifetime": [],
                   "immersion": [],
                   "extern": []}

        for response in sqlResponse:
            dataset["id"].append(response[0])
            dataset["release_date"].append(response[1])
            dataset["genres"].append(response[2])
            dataset["price"].append(response[3])
            dataset["currency"].append(response[4])
            dataset["age"].append(response[5])
            dataset["windows"].append(response[6])
            dataset["mac"].append(response[7])
            dataset["linux"].append(response[8])
            dataset["publishers"].append(response[9])
            dataset["developers"].append(response[10])
            dataset["graphic"].append(response[11])
            dataset["gameplay"].append(response[12])
            dataset["lifetime"].append(response[13])
            dataset["immersion"].append(response[14])
            dataset["extern"].append(response[15])

        return dataset

    @staticmethod
    def hashColumn(col):

        hashs = []

        for ele in col:
            hashs.append(abs(hash(ele)) % (10 ** 8))

        return hashs

    @staticmethod
    def datesToTimestamp(dateList):

        timestamps = []

        for date in dateList:
            timestamps.append(date.timestamp())

        return timestamps

    @staticmethod
    def convertPrices(prices, currencies, currencyTarget):

        conertPrices = []
        converter = CurrencyConverter()

        for i in range(len(prices)):

            if currencies[i] not in converter.currencies:
                print("INFO: {} non pris en charge.".format(currencies[i]))

            conertPrices.append(converter.convert(prices[i], currencies[i], currencyTarget))

        return conertPrices
