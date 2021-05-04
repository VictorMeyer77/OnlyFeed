from psycopg2 import pool
from datetime import datetime
import requests
import json
import sys
import re


class GameAlim:

    def __init__(self, confSteamLink, confPostgres):

        self.listLink = confSteamLink["game_list_link"]
        self.infoLink = confSteamLink["game_info_link"]

        try:

            self.pool = pool.SimpleConnectionPool(1, 10, host=confPostgres["host"],
                                                  port=confPostgres["port"],
                                                  dbname=confPostgres["database"],
                                                  user=confPostgres["user"],
                                                  password=confPostgres["password"])

        except Exception as e:

            print("ERROR: Impossible de se connecter à la base de données")
            print(e)
            sys.exit()

    def run(self, count):

        gameIds = self.getNewGameIds()

        i = 0
        while i < count:

            info = self.getSteamGameInfo(gameIds[i])

            if info is not None:
                self.insertSteamGame(self.formatGameInfo(info))
            else:
                count += 1

            i += 1

    @staticmethod
    def formatGameInfo(gameInfo):

        htmlRegex = re.compile("<.*?>")

        gameId = gameInfo["steam_appid"]
        name = gameInfo["name"]
        age = int(gameInfo["required_age"])

        if "supported_languages" in gameInfo.keys():
            languages = gameInfo["supported_languages"]
        else:
            languages = ""

        windows = gameInfo["platforms"]["windows"]
        mac = gameInfo["platforms"]["mac"]
        linux = gameInfo["platforms"]["linux"]

        if gameInfo["pc_requirements"]:
            windows_requirements = re.sub(htmlRegex, "", gameInfo["pc_requirements"]["minimum"]).replace("\t", " ")
        else:
            windows_requirements = ""

        if gameInfo["mac_requirements"]:
            mac_requirements = re.sub(htmlRegex, "", gameInfo["mac_requirements"]["minimum"]).replace("\t", " ")
        else:
            mac_requirements = ""

        if gameInfo["linux_requirements"]:
            linux_requirements = re.sub(htmlRegex, "", gameInfo["linux_requirements"]["minimum"]).replace("\t", " ")
        else:
            linux_requirements = ""

        publishers = ",".join(gameInfo["publishers"])
        developers = ",".join(gameInfo["developers"])

        if "price_overview" not in gameInfo.keys():
            price = 0
            currency = "EUR"
        else:
            price = gameInfo["price_overview"]["final"]
            currency = gameInfo["price_overview"]["currency"]

        categories = []
        for c in gameInfo["categories"]:
            categories.append(c["description"])

        categories = ",".join(categories)

        genres = []
        for g in gameInfo["genres"]:
            genres.append(g["description"])

        genres = ",".join(genres)

        if "recommendations" in gameInfo.keys():
            recommendations = gameInfo["recommendations"]["total"]
        else:
            recommendations = 0

        try:
            release_date = str(datetime.strptime(gameInfo["release_date"]["date"], "%d %b, %Y"))

        except Exception:
            release_date = "1970-01-01 00:00:00"

        return (gameId,
                name,
                age,
                languages,
                windows,
                mac,
                linux,
                windows_requirements,
                mac_requirements,
                linux_requirements,
                publishers,
                developers,
                price,
                currency,
                categories,
                genres,
                recommendations,
                release_date)

    def getNewGameIds(self):

        steamGameIds = self.getSteamGameIds()
        pgGameIds = self.getPgGameIds()
        newGameIds = []

        for gameId in steamGameIds:

            if gameId not in pgGameIds and gameId not in newGameIds:
                newGameIds.append(gameId)

        return newGameIds

    # STEAM API

    def getSteamGameIds(self):

        gameListReq = requests.get(self.listLink)
        gameListResponse = json.loads(gameListReq.content)
        ids = []

        for game in gameListResponse["applist"]["apps"]:
            ids.append(game["appid"])

        return list(set(ids))

    def getSteamGameInfo(self, gameId):

        gameInfoReq = requests.get(self.infoLink + str(gameId))
        gameInfoResponse = json.loads(gameInfoReq.content)

        if gameInfoResponse[str(gameId)]["success"]:
            return gameInfoResponse[str(gameId)]["data"]
        else:
            return None

    # POSTGRES

    def getPgGameIds(self):

        try:

            ids = []
            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("select id from steam_video_games")
            resultReq = cursor.fetchall()

            for gameId in resultReq:
                ids.append(gameId[0])

            self.pool.putconn(conn)
            return ids

        except Exception as e:

            print("ERROR getPgGameIds: " + str(e))
            sys.exit()

    def insertSteamGame(self, info):

        try:

            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO steam_video_games (id,"
                           "name,"
                           "age,"
                           "languages,"
                           "windows,"
                           "mac,"
                           "linux,"
                           "windows_requirements,"
                           "mac_requirements,"
                           "linux_requirements,"
                           "publishers,"
                           "developers,"
                           "price,"
                           "currency,"
                           "categories,"
                           "genres,"
                           "recommendations,"
                           "release_date)"
                           "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", info)

            cursor.execute("INSERT INTO steam_game_reviews_flag (game_id, flag, date_maj) VALUES (%s, %s, %s)",
                           (info[0], "*", str(datetime.now())))

            conn.commit()
            self.pool.putconn(conn)

        except Exception as e:

            print("ERROR insertSteamGame: " + str(e))
            sys.exit()
