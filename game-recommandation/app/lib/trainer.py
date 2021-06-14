from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import normalize
from sklearn.cluster import DBSCAN
from joblib import dump, load
from datetime import datetime
from .postgresDao import PostgresDao
import numpy as np
import os


class Trainer:

    def __init__(self, modelType, nearestNeightboor, alpha, minGameByCat, outputDir, postgresDao, default=False):

        self.nearestNeightboor = nearestNeightboor
        self.alpha = alpha
        self.minGameByCat = minGameByCat
        self.outputDir = outputDir
        self.postgresDao = postgresDao
        self.modelType = modelType
        self.default = default
        self.modelName = self.getModelName()

    def run(self, dataset):

        model, pred = self.clusterize(dataset)

        if model is not None and pred is not None:
            self.saveModel(model)
            self.postgresDao.insertModel(self.modelName, self.modelType, self.nearestNeightboor,
                                         self.alpha, self.minGameByCat)

    def clusterize(self, dataset, model=None):

        datasetNoId = dataset[1:, :].T
        normData = normalize(datasetNoId, axis=0)

        if model is None:
            bestEps = self.searchBestEps(datasetNoId)

            if bestEps < 0.0000000001:

                print("ERROR: eps {} est une valeur négative. Paramètres invalides.".format(bestEps))
                model = None
                pred = None

            else:

                model = DBSCAN(eps=bestEps, min_samples=self.minGameByCat)
                pred = model.fit_predict(normData)

        else:

            pred = model.fit_predict(normData)

        return model, pred

    def searchBestEps(self, dataset):

        network = NearestNeighbors(n_neighbors=self.nearestNeightboor)
        normData = normalize(dataset, axis=0)
        neightboors = network.fit(normData)
        distances, indices = neightboors.kneighbors(normData)
        nearNeight = np.array([distances[:, 1], range(len(distances))])
        sortNearNeight = nearNeight[:, nearNeight[0].argsort()]
        sizeMin = int(len(distances) * (1.0 - (100 - self.alpha) / 100)) - 1

        return nearNeight[0, int(sortNearNeight[1, sizeMin])]

    def loadModel(self, name):

        return load(os.path.join(self.outputDir, name + ".joblib"))

    def saveModel(self, model):

        dump(model, os.path.join(self.outputDir, self.modelName + ".joblib"))

    def getModelName(self):

        return "model_" + str(int(datetime.now().timestamp())) if not self.default else "default"
