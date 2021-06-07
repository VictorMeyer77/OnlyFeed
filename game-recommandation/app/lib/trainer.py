from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import normalize
from sklearn.cluster import DBSCAN
from joblib import dump, load
from datetime import datetime
from .dataFormater import cleanGameData
from .postgresDao import PostgresDao
import numpy as np
import os


class Trainer:

    def __init__(self, modelType, nearestNeightboor, alpha, minGameByCat, outputDir, postgresDao):

        self.modelType = modelType
        self.nearestNeightboor = nearestNeightboor
        self.alpha = alpha
        self.minGameByCat = minGameByCat
        self.outputDir = outputDir
        self.postgresDao = postgresDao

    def chooseModels(self):

        models = self.postgresDao.getModels(self.modelType)

        if len(models["name"]) < 1:

            dictData = self.postgresDao.getGameDataset()
            dataset = cleanGameData(dictData)
            model, pred = self.clusterize(dataset)
            modelName = "default"
            self.saveModel(model, True)
            self.postgresDao.insertModel("default", 0, self.nearestNeightboor, self.alpha, self.minGameByCat)

        elif len(models["name"]) > 1:

            bestModelName = models["name"][0]
            bestModelNote = models["note"][0]

            for i in range(1, len(models["name"])):

                if models["note"][i] > bestModelNote and models["nb_test"][i] > 4:
                    bestModelNote = models["note"][i]
                    bestModelName = models["name"][i]

            model = self.loadModel(bestModelName)
            modelName = bestModelName

        else:

            model = self.loadModel("default")
            modelName = "default"

        return model, modelName

    def clusterize(self, dataset):

        dataset = dataset[1:, :].T
        bestEps = self.searchBestDelta(dataset)
        normData = normalize(dataset, axis=0)
        dbscan = DBSCAN(eps=bestEps, min_samples=self.minGameByCat)
        pred = dbscan.fit_predict(normData)

        return dbscan, pred

    def searchBestDelta(self, dataset):

        network = NearestNeighbors(n_neighbors=self.nearestNeightboor)
        normData = normalize(dataset, axis=0)
        neightboors = network.fit(normData)
        distances, indices = neightboors.kneighbors(normData)
        nearNeight = np.array([distances[:, 1], range(len(distances))])
        sortNearNeight = nearNeight[:, nearNeight[0].argsort()]
        sizeMin = int(len(distances) * (1.0 - (100 - self.alpha) / 100))

        return nearNeight[0, int(sortNearNeight[1, sizeMin])]

    def loadModel(self, name):

        return load(os.path.join(self.outputDir, name + ".joblib"))

    def saveModel(self, model, default=False):

        fileName = "model_" + str(
            int(datetime.now().timestamp() / 1000)) + ".joblib" if not default else "default.joblib"
        dump(model, os.path.join(self.outputDir, fileName))
