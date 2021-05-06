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

            print("INFO: Connection établie avec {}.".format(confPostgres["database"]))

        except Exception as e:

            print("ERROR: Impossible de se connecter à la base de données")
            print(e)
            sys.exit()

    def run(self, count):

        gameIds = self.getNewGameIds()

        i = 0
        while i < count and i < len(gameIds):

            info = self.getSteamGameInfo(gameIds[i])

            if info is not None:
                self.insertSteamGame(self.formatGameInfo(info))
            else:
                self.insertSteamInvalidGame(gameIds[i])
                count += 1

            i += 1

    @staticmethod
    def formatGameInfo(gameInfo):

        htmlRegex = re.compile("<.*?>")

        gameId = gameInfo["steam_appid"]
        name = gameInfo["name"]
        age = int(gameInfo["required_age"])
        windows = gameInfo["platforms"]["windows"]
        mac = gameInfo["platforms"]["mac"]
        linux = gameInfo["platforms"]["linux"]

        if "publishers" in gameInfo.keys():
            publishers = ",".join(gameInfo["publishers"])
        else:
            publishers = ""

        if "developers" in gameInfo.keys():
            developers = ",".join(gameInfo["developers"])
        else:
            developers = ""

        if "supported_languages" in gameInfo.keys():
            languages = gameInfo["supported_languages"]
        else:
            languages = ""

        if "pc_requirements" in gameInfo.keys() and \
                gameInfo["pc_requirements"] != [] and \
                "minimum" in gameInfo["pc_requirements"].keys():
            windows_requirements = re.sub(htmlRegex, "", gameInfo["pc_requirements"]["minimum"]).replace("\t", " ")
        else:
            windows_requirements = ""

        if "mac_requirements" in gameInfo.keys() and \
                gameInfo["mac_requirements"] != [] and \
                "minimum" in gameInfo["mac_requirements"].keys():
            mac_requirements = re.sub(htmlRegex, "", gameInfo["mac_requirements"]["minimum"]).replace("\t", " ")
        else:
            mac_requirements = ""

        if "linux_requirements" in gameInfo.keys() and \
                gameInfo["linux_requirements"] != [] and \
                "minimum" in gameInfo["linux_requirements"].keys():
            linux_requirements = re.sub(htmlRegex, "", gameInfo["linux_requirements"]["minimum"]).replace("\t", " ")
        else:
            linux_requirements = ""

        if "price_overview" not in gameInfo.keys():
            price = 0
            currency = "EUR"
        else:
            price = gameInfo["price_overview"]["final"]
            currency = gameInfo["price_overview"]["currency"]

        if "categories" in gameInfo.keys():

            categories = []
            for c in gameInfo["categories"]:
                categories.append(c["description"])

            categories = ",".join(categories)
        else:
            categories = ""

        if "genres" in gameInfo.keys():

            genres = []
            for g in gameInfo["genres"]:
                genres.append(g["description"])

            genres = ",".join(genres)
        else:
            genres = ""

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
        pgInvalidIds = self.getPgInvalidGameIds()
        newGameIds = []

        for gameId in steamGameIds:

            if gameId not in pgGameIds and gameId not in pgInvalidIds:
                newGameIds.append(gameId)

        return list(set(newGameIds))

    # STEAM API

    def getSteamGameIds(self):

        gameListReq = requests.get(self.listLink)
        gameListResponse = json.loads(gameListReq.content)
        ids = []

        for game in gameListResponse["applist"]["apps"]:
            ids.append(game["appid"])

        return list(set(ids))

    def getSteamGameInfo(self, gameId):

        try:
            gameInfoReq = requests.get(self.infoLink + str(gameId))
            gameInfoResponse = json.loads(gameInfoReq.content)

            if gameInfoResponse[str(gameId)]["success"]:
                return gameInfoResponse[str(gameId)]["data"]

        except Exception as e:

            print("ERROR getSteamGameInfo: {}".format(str(e)))
            return None

    # POSTGRES

    def getPgGameIds(self):

        conn = None

        try:

            ids = []
            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("select id from steam_video_games")
            resultReq = cursor.fetchall()

            for gameId in resultReq:
                ids.append(gameId[0])

            return ids

        except Exception as e:

            print("ERROR getPgGameIds: " + str(e))

        finally:

            if conn is not None:
                self.pool.putconn(conn)

    def getPgInvalidGameIds(self):

        conn = None

        try:

            ids = []
            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("select id from steam_invalid_game_ids")
            resultReq = cursor.fetchall()

            for gameId in resultReq:
                ids.append(gameId[0])

            return ids

        except Exception as e:

            print("ERROR getPgInvalidGameIds: " + str(e))

        finally:

            if conn is not None:
                self.pool.putconn(conn)

    def insertSteamGame(self, info):

        conn = None

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
            print("INFO: {} inséré dans la base de données.".format(info[1]))

        except Exception as e:

            print("ERROR insertSteamGame: " + str(e))

        finally:

            if conn is not None:
                self.pool.putconn(conn)

    def insertSteamInvalidGame(self, gameId):

        conn = None

        try:

            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO steam_invalid_game_ids (id) VALUES (%s)", (gameId,))
            conn.commit()
            print("INFO: {} Id invalide inséré dans la base de données.".format(str(gameId)))

        except Exception as e:

            print("ERROR insertSteamInvalidGame: " + str(e))

        finally:

            if conn is not None:
                self.pool.putconn(conn)
