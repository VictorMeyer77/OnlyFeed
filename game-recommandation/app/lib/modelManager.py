from .dataFormater import cleanGameData
from .trainer import Trainer
from random import randint
import numpy as np
import os


class ModelManager:

    def __init__(self, postgresDao, modelType, confModels, outputDir):

        self.postgresDao = postgresDao
        self.modelType = modelType
        self.confModels = confModels
        self.nearestNeightboor = confModels["defaultNearestNeightboor"]
        self.alpha = confModels["defaultAlpha"]
        self.minGameByCat = confModels["defaultMinGameByCat"]
        self.outputDir = outputDir

    def chooseModels(self):

        models = self.postgresDao.getModels(self.modelType)
        trainer = Trainer(self.modelType, self.nearestNeightboor, self.alpha, self.minGameByCat, self.outputDir,
                          self.postgresDao, True)

        if len(models["name"]) < 1:

            dictData = self.postgresDao.getGameDataset()
            dataset = cleanGameData(dictData)
            model, pred = trainer.run(dataset)
            modelName = "default"

        elif len(models["name"]) > 1:

            bestModelName = models["name"][0]
            bestModelNote = models["note"][0]

            for i in range(1, len(models["name"])):

                if models["note"][i] > bestModelNote and models["nb_test"][i] > 4:
                    bestModelNote = models["note"][i]
                    bestModelName = models["name"][i]

            model = trainer.loadModel(bestModelName)
            modelName = bestModelName

        else:

            model = trainer.loadModel("default")
            modelName = "default"

        return model, modelName

    def trainNewModels(self, nbModel):

        existModels = self.postgresDao.getModels(0)
        dictData = self.postgresDao.getGameDataset()
        dataset = cleanGameData(dictData)
        print(existModels)
        newModels = []

        while len(newModels) < nbModel:

            if len(existModels) + len(newModels) >= \
                    (self.confModels["nearestNeightboor"][1] - self.confModels["nearestNeightboor"][0]) / \
                    self.confModels["nearestNeightboor"][2] \
                    + (self.confModels["alpha"][1] - self.confModels["alpha"][0]) / self.confModels["alpha"][2] \
                    + (self.confModels["minGameByCat"][1] - self.confModels["minGameByCat"][0]) / \
                    self.confModels["minGameByCat"][2]:

                print("WARNING: Plus aucune combinaison de paramètres possible")
                break

            else:

                newModel = self.getRandomParam()
                if not self.isParamAlreadyExist(newModel, existModels):
                    newModels.append(newModel)

            for newModel in newModels:
                trainer = Trainer(self.modelType, newModels[0], newModels[1], newModel[2], self.outputDir,
                                  self.postgresDao, False)
                trainer.run(dataset)

        print(newModels)

    def createModelTest(self, dataset, pred, idModel):

        testGameIndex = np.where(pred != -1)[randint(0, len(np.where(pred != -1)) - 1)]
        testGameId = dataset[0][testGameIndex]
        testCat = pred[testGameIndex]

        nearGameIndexs = np.delete(np.where(pred == testCat), testGameIndex)
        nearGameId = dataset[0][nearGameIndexs[randint(0, len(nearGameIndexs) - 1)]]

        indexGameOne = randint(0, len(np.where(pred != testCat & pred != -1)) - 1)
        idGameOne = dataset[0][np.where(pred != testCat & pred != -1)[indexGameOne]]
        catGameOne = pred[indexGameOne]

        indexGameTwo = randint(0, len(np.where(pred != testCat & pred != -1 & pred != catGameOne)) - 1)
        idGameTwo = dataset[0][np.where(pred != testCat & pred != -1 & pred != catGameOne)[indexGameTwo]]

        self.postgresDao.insertModelTest(idModel, testGameId, nearGameId, idGameOne, idGameTwo)

    def generateTestForModels(self, nbTestForModel):

        trainer = Trainer(self.modelType, self.nearestNeightboor, self.alpha, self.minGameByCat, self.outputDir,
                          self.postgresDao)

        dictData = self.postgresDao.getGameDataset()
        dataset = cleanGameData(dictData)

        for file in os.listdir(self.outputDir):

            if file != ".gitignore":
                modelName = file.replace(".joblib", "")

                model = trainer.loadModel(modelName)
                model, pred = trainer.clusterize(dataset, model)
                idModel = self.postgresDao.getModelIdByName(modelName)

                for i in range(nbTestForModel):

                    self.createModelTest(dataset, pred, idModel)

    def updateModelRates(self):

        modelIds = self.postgresDao.getModelIds()

        for modelId in modelIds:

            rates = self.postgresDao.getModelRatesById(modelId)
            avg = np.average(np.array(rates))
            self.postgresDao.updateModelRecRate(modelId, avg, len(rates))

    def getRandomParam(self):

        randBuffer = randint(self.confModels["nearestNeightboor"][0], self.confModels["nearestNeightboor"][1])
        neirNeight = int(randBuffer - (randBuffer % self.confModels["nearestNeightboor"][2]))
        randBuffer = randint(self.confModels["alpha"][0], self.confModels["alpha"][1])
        alpha = int(randBuffer - (randBuffer % self.confModels["alpha"][2]))
        randBuffer = randint(self.confModels["minGameByCat"][0], self.confModels["minGameByCat"][1])
        minGameByCat = int(randBuffer - (randBuffer % self.confModels["minGameByCat"][2]))

        return neirNeight, alpha, minGameByCat

    @staticmethod
    def isParamAlreadyExist(params, existModels):

        for i in range(len(existModels["near_neight"])):

            if existModels["near_neight"][i] == params[0] and \
                    existModels["alpha"][i] == params[1] and \
                    existModels["min_game_by_cat"][i] == params[2]:
                return True

        return False
