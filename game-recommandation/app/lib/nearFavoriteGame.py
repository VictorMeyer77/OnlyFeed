from sklearn.preprocessing import normalize
from sklearn.neighbors import DistanceMetric
from .dataFormater import cleanGameData
import numpy as np
from lib.trainer import Trainer


class NearFavoriteGame:

    def __init__(self, postgresDao, outputDir, nearestNeightboor, alpha, minGameByCat):

        self.postgresDao = postgresDao
        self.trainer = Trainer(0, nearestNeightboor, alpha, minGameByCat, outputDir, self.postgresDao)

        self.run()

    def run(self):

        model, modelName = self.trainer.chooseModels()
        dataset, pred = self.getGameDatasetWithPred(model)
        distancePerGroup = self.distancePerGroup(dataset, pred)
        print(distancePerGroup)
        print(model)
        print(modelName)
        userIds = self.postgresDao.getOfUserId()
        evals = self.postgresDao.getGameUserEvaluation()

        for userId in userIds:
            userEval = self.getUserGameEval(userId, evals)
            print(userEval)

        print(self.getUserGameEval(1, evals))

    def getGameDatasetWithPred(self, model):

        dictData = self.postgresDao.getGameDataset()
        dataset = cleanGameData(dictData)
        formatData = dataset[1:, :].T
        normData = normalize(formatData, axis=0)
        pred = model.fit_predict(normData)

        return dataset, pred

    @staticmethod
    def getUserGameEval(userId, evals):

        userEvals = []

        for i in range(len(evals["of_user_id"])):

            if evals["of_user_id"][i] == userId:
                userEvals.append((evals["game_id"][i], evals["rate"][i]))

        return userEvals

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
