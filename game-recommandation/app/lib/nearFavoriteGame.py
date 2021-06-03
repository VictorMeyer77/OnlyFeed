from lib.postgresDao import PostgresDao
from datetime import datetime
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import normalize
from sklearn.cluster import DBSCAN
from sklearn.neighbors import DistanceMetric
from currency_converter import CurrencyConverter
import numpy as np
from joblib import dump, load
from datetime import datetime


class NearFavoriteGame:

    def __init__(self, postgresDao, nearestNeightboor, priceCurrency="EUR"):

        self.postgresDao = postgresDao
        self.priceCurrency = priceCurrency

        sqlData = self.postgresDao.getGameDataset()
        dataset = self.cleanData(sqlData)
        dataset = np.delete(dataset, 1, axis=0)
        model, pred = self.clusterize(dataset, nearestNeightboor, 90, 10)
        self.distancePerGroup(dataset, pred)

    def cleanData(self, sqlData):

        dictData = self.extractDataset(sqlData)
        dictData["price"] = self.convertPrices(dictData["price"], dictData["currency"], self.priceCurrency)
        dictData["release_date"] = self.datesToTimestamp(dictData["release_date"])
        dictData["genres"] = self.getFirstListItem(dictData["genres"])
        dictData["genres"] = self.hashColumn(dictData["genres"])
        dictData["publishers"] = self.hashColumn(dictData["publishers"])
        dictData["developers"] = self.getFirstListItem(dictData["developers"])
        dictData["developers"] = self.hashColumn(dictData["developers"])

        del dictData["currency"]

        return np.array(list(dictData.values())).astype("float64")

    def clusterize(self, dataset, nearestNeightboor, alpha, minGameByCat):

        dataset = dataset[1:, :].T
        bestEps = self.searchBestDelta(dataset, nearestNeightboor, alpha)
        normData = normalize(dataset, axis=0)
        dbscan = DBSCAN(eps=bestEps, min_samples=minGameByCat)
        pred = dbscan.fit_predict(normData)

        return dbscan, pred

    @staticmethod
    def distancePerGroup(dataset, pred):

        distancesCountPerClass = {}
        unique, counts = np.unique(pred, return_counts=True)

        for classe in unique:

            distancesCountPerClass[classe] = {}

            for distClasse in unique:
                distancesCountPerClass[classe][distClasse] = 0

        normData = normalize(dataset[1:, :].T, axis=0)
        distanceCalc = DistanceMetric.get_metric("minkowski")
        distances = distanceCalc.pairwise(normData)

        for i in range(distances.shape[0]):

            minDist, ind = 10000.0, -1

            for j in range(distances.shape[0]):

                if i == j or pred[i] == pred[j] or pred[j] == -1:
                    continue

                if distances[i][j] < minDist:
                    minDist = distances[i][j]
                    ind = j

            distancesCountPerClass[pred[i]][pred[ind]] += 1

        for i in distancesCountPerClass.keys():

            tot = sum(list(distancesCountPerClass[i].values()))

            for j in distancesCountPerClass[i].keys():
                distancesCountPerClass[i][j] = float(distancesCountPerClass[i][j]) / tot

        return distancesCountPerClass

    def loadModel(self):

        return load()

    @staticmethod
    def saveModel(model, outputDir):

        fileName = "model_" + str(int(datetime.now().timestamp() / 1000)) + ".joblib"
        dump(model, outputDir, fileName)

    @staticmethod
    def searchBestDelta(dataset, nearestNeightboor, alpha):

        network = NearestNeighbors(n_neighbors=nearestNeightboor)
        normData = normalize(dataset, axis=0)
        neightboors = network.fit(normData)
        distances, indices = neightboors.kneighbors(normData)
        nearNeight = np.array([distances[:, 1], range(len(distances))])
        sortNearNeight = nearNeight[:, nearNeight[0].argsort()]
        sizeMin = int(len(distances) * (1.0 - (100 - alpha) / 100))

        return nearNeight[0, int(sortNearNeight[1, sizeMin])]

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
    def getFirstListItem(column):

        firsts = []

        for ele in column:
            firsts.append(ele.split(",")[0])

        return firsts

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
