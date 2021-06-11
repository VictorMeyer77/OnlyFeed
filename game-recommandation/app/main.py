from lib.postgresDao import PostgresDao
from lib.nearFavoriteGame import NearFavoriteGame
from lib.trainer import Trainer
import json
import sys

if __name__ == "__main__":

    conf = None

    try:

        file = open("../conf/configuration.json", "r")
        conf = json.load(file)

    except Exception as e:

        print("ERROR: " + str(e))
        sys.exit()

    postgresDao = PostgresDao(conf["postgres"])
    trainer = Trainer(0, 10, 90, 20, conf["modelsDir"], postgresDao, conf["modelParams"])
    #NearFavoriteGame(postgresDao, trainer, 5)
    trainer.trainNewModels(3)