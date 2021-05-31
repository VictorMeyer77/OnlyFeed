from psycopg2 import pool
import sys

class PostgresDao:

    def __init__(self, confPostgres):

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

    def getGameDataset(self):

        conn = None

        try:

            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("""select vg.id,
                           vg.release_date,
                           vg.genres,
                           vg.price,
                           vg.currency,
                           vg.age,
                           vg.windows,
                           vg.mac,
                           vg.linux,
                           vg.publishers,
                           vg.developers,
                           ga.graphic,
                           ga.gameplay,
                           ga.lifetime,
                           ga.immersion,
                           ga.extern
                           from (select distinct id_game, date_maj, graphic, gameplay, lifetime,
                           immersion, extern from of_game_analysis order by date_maj desc) as ga
                           left join steam_video_games as vg ON ga.id_game = vg.id""")

            resultReq = cursor.fetchall()

            return resultReq

        except Exception as e:

            print("ERROR getPgGameIds: " + str(e))

        finally:

            if conn is not None:
                self.pool.putconn(conn)