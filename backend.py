import sqlite3
from flask import g

DATABASE = './maindatabase.db'


def get_db():
    """Return database"""
    db = getattr(g, '_database', None)
    if(db is None):
        db = g._database = sqlite3.connect(DATABASE)
    return db


def make_dicts(cursor: sqlite3.Cursor, row: sqlite3.Row):
    """Return data from querry as dictionary"""
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


def query_db(query: str, args=(), one=None):
    """Return result of query"""
    if one is None:
        one = True
    else:
        one = False
    cursor = get_db().execute(query, args)
    result = cursor.fetchall()
    cursor.close()
    return (result[0] if result else None) if one else result


def get_all_marks():
    """Return all marks for instructors"""
    return query_db("""SELECT User.username,Assignment1,Assignment2,
                    Assignment3, Assignment4, Midterm, FinalTest
                    FROM User INNER JOIN StudentMark
                    WHERE isInstructor==0
                    AND User.username == StudentMark.username;""",
                    (), one=False)


def get_student_marks(username: str):
    """Return username marks"""
    return query_db(""""SELECT * FROM StudentMark
                    WHERE StudentMark.username == ?;""",
                    args=(username), one=True)


def get_feedback(username: str):
    """Return feedback by instructor"""
    return query_db("""SELECT * FROM Feedback
                    WHERE Feedback.username == ?;""",
                    args=(username), one=False)


def get_regrade_requests():
    """Return all regrade requests"""
    return query_db("""SELECT * FROM RegradeRequests;""", (), one=False)


def isUser(username: str, password: str):
    """Return True if username is in database"""
    result = query_db("""SELECT username FROM User WHERE User.username == ?
                    AND User.password == ?;""",
                      args=(username, password))
    if result is None:
        return False
    return True


def isInstructor(username: str):
    """Return true if username is instructor"""
    result = query_db("""SELECT username FROM User WHERE User.username == ?
                    AND User.isInstructor == 1;""",
                      args=(username))
    if result is None:
        return False
    return True


def addUser(username: str, password: str, isInstructor: int):
    """Insert username to database"""
    query_db("""INSERT INTO User VALUES (?,?,?);""",
             arg=(username, password, isInstructor))


def addUserMarks(username: str):
    """Add username marks to database"""
    query_db("""INSERT INTO StudentMark
    VALUES (?,?,?,?,?,?,?);""", args=(username, 0, 0, 0, 0, 0, 0, 0))


def addFeedback(username: str, content: str):
    """Add content to database"""
    query_db("""INSERT INTO Feedback VALUES (?,?);""",
             args=(username, content))


def addRegradeRequest(username: str, content: str):
    """Add regrade request to database"""
    query_db("""INSERT INTO RegradeRequests VALUES (?, ?);""",
             args=(username, content))


def updateUserMarks(username: str, marks: [int]):
    """Update user marks"""
    query_db("""UPDATE StudentMark SET StudentMark.Assignment1 = ?,
    StudentMark.Assignment2 = ?,StudentMark.Assignment3 = ?
    ,StudentMark.Assignment4 = ?,StudentMark.Midterm = ?
    ,StudentMark.FinalTest = ? WHERE StudentMark.username == ?;""",
             args=(username, marks))
