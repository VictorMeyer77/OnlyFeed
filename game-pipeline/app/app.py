from lib.steamApi import *
from lib.gameAlim import *
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

    GameAlim(conf["steam_link"], conf["postgres"]).launchAlim(10)