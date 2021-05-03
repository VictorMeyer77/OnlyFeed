from lib.gameAlim import GameAlim
from lib.gameReviewAlim import GameReviewAlim
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

    if len(sys.argv) < 2:
        print("ERROR: Specify command: game or review")
        sys.exit()

    if sys.argv[1] == "game":

        if len(sys.argv) < 3:

            print("ERROR: game prend un argument. Le nombre de jeux à insérér")
            sys.exit()

        else:

            GameAlim(conf["steam_link"], conf["postgres"]).run(int(sys.argv[2]))

    elif sys.argv[1] == "review":

        if len(sys.argv) < 3:

            print("ERROR: review prend un argument. Le nombre d'avis à insérér")
            sys.exit()

        else:

            GameReviewAlim(conf["steam_link"], conf["postgres"]).run(int(sys.argv[2]))

    else:

        print("ERROR: Specify command \"game\" or \"review\"")