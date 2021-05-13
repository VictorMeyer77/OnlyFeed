from lib.gameRating import GameRating
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

    GameRating(conf["postgres"]).run()