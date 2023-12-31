# взаимодействие с БД

import sqlite3

connection = sqlite3.connect("base.sqlite")
cur = connection.cursor()


def create_team(t_name):
    f = cur.execute("""SELECT id FROM teams WHERE name = ?""", (t_name,)).fetchone()
    if f:
        return False
    cur.execute("""INSERT INTO teams (name, score, ending_quests) VALUES (?, 0, 0)""", (t_name,))
    connection.commit()
    return True


def add_team_member(user_id, name, t_name):
    f = cur.execute("""SELECT id FROM teams WHERE name = ?""", (t_name,)).fetchone()
    if not f:
        return False
    f = cur.execute("""SELECT name FROM users WHERE user_id = ?""", (user_id,)).fetchone()
    if f:
        cur.execute("""DELETE FROM users WHERE user_id = ?""", (user_id,))
        connection.commit()
    recv = """INSERT INTO users SELECT ?, ?, (
    SELECT id FROM teams WHERE name = ?)"""
    cur.execute(recv, (user_id, name, t_name))
    connection.commit()
    return True


def update_score(user_id, sc_change):
    recv = """UPDATE teams 
    SET score = score + ?,
    ending_quests = ending_quests + 1
    WHERE id = (
    SELECT team FROM users 
    WHERE user_id = ?)"""

    cur.execute(recv, (sc_change, user_id))
    connection.commit()


def get_rating():
    recv = """SELECT name, score, ending_quests FROM teams
    WHERE ending_quests != 0
    ORDER BY score / ending_quests LIMIT 10"""

    return cur.execute(recv).fetchall()

