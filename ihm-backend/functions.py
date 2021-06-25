import datetime
import psycopg2
from config import POSTGRES

conn = psycopg2.connect( host=POSTGRES['host'], user=POSTGRES['user'], password=POSTGRES['pw'], dbname=POSTGRES['db'])

def days_between(d1, d2):
    return abs((d2 - d1).days)

def get_games_to_compare(id_user):
    games = {}
    cur = conn.cursor()
    cur.execute('SELECT id_game_test, id_game_one, id_game_two, id_game_three FROM of_test_game_similarity WHERE id_game_test NOT IN (SELECT id_test FROM of_similarity_test_result WHERE id_user = '+str(id_user)+') ORDER BY date_create DESC LIMIT 1')
    result = cur.fetchall()

    for i in range(4):
        cur.execute('SELECT name FROM steam_video_games WHERE id = ' + str(result[0][i]))
        game_name = cur.fetchall()
        if i == 0:
            games["test_game"] = {}
            games["test_game"][result[0][i]] = game_name[0][0]
        else:
            games["game" + str(i)] = {}
            games["game" + str(i)][result[0][i]] = game_name[0][0]

    return games

def save_user_comparison(id_user, id_game, result):
    
    try:
        date_create = datetime.datetime.now()
        cur = conn.cursor()
        cur.execute("INSERT INTO of_similarity_test_result(id_test, id_user, result, date_create) VALUES("+ str(id_game) +", "+ str(id_user) +", "+ str(result) +", '"+ str(date_create) +"')")
        conn.commit()
    except:
        return 0
    return 1
