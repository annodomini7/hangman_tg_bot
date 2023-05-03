import sqlite3
from constants import database_path


def get_result(chat_id: int):
    """get tuple (num_games, win, lose) for user from database"""
    init_user(chat_id)
    con = sqlite3.connect(database_path)
    cur = con.cursor()
    res = cur.execute(f"SELECT num_games, win, lose FROM results WHERE id={chat_id}").fetchall()
    cur.close()
    # print(res[0][0])
    return res[0]


def set_result(chat_id: int, win=False, lose=False):
    """increase win or lose for chat_id"""
    init_user(chat_id)
    con = sqlite3.connect(database_path)
    cur = con.cursor()
    current = get_result(chat_id)
    if win:
        cur.execute(f"UPDATE results SET num_games = {current[0] + 1}, win = {current[1] + 1}")
    if lose:
        cur.execute(f"UPDATE results SET num_games = {current[0] + 1}, lose = {current[2] + 1}")
    con.commit()
    cur.close()


def init_user(chat_id: int):
    """if chat_id not in database this function creates it"""
    con = sqlite3.connect(database_path)
    cur = con.cursor()
    res = cur.execute(f"SELECT * FROM results WHERE id={chat_id}")
    if res.fetchone() is None:
        cur.execute(f"INSERT INTO results VALUES({chat_id}, 0, 0, 0)")
        con.commit()
    cur.close()
