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
        self.fileName = self.getFileName()

    def run(self, dataset):

        model, pred = self.clusterize(dataset)
        self.saveModel(model)
        self.postgresDao.insertModel(self.fileName, self.modelType, self.nearestNeightboor,
                                     self.alpha, self.minGameByCat)

    def clusterize(self, dataset):
        dataset = dataset[1:, :].T
        bestEps = self.searchBestEps(dataset)
        normData = normalize(dataset, axis=0)
        dbscan = DBSCAN(eps=bestEps, min_samples=self.minGameByCat)
        pred = dbscan.fit_predict(normData)

        return dbscan, pred

    def searchBestEps(self, dataset):
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

    def saveModel(self, model):

        dump(model, os.path.join(self.outputDir, self.fileName))

    def getFileName(self):

        return "model_" + str(int(datetime.now().timestamp() / 1000)) + ".joblib" \
            if not self.default else "default.joblib"
