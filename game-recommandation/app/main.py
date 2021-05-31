from lib.postgresDao import PostgresDao
from lib.nearFavoriteGame import NearFavoriteGame
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
    NearFavoriteGame(postgresDao, 10, 0.4)
