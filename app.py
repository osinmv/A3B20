from flask import Flask, render_template, url_for, request, redirect, g, session
import sqlite3
DATABASE = './assignment3.db'

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


def update_db(query: str, args=()):
    """Updates database and does not return a result"""
    cursor = get_db().execute(query, args)
    get_db().commit()
    cursor.close()


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
    return query_db("""SELECT * FROM StudentMark
                    WHERE StudentMark.username == ?;""",
                    (username,), one=True)


def get_feedback(username: str):
    """Return feedback by instructor"""
    return query_db("""SELECT * FROM Feedback
                    WHERE Feedback.username == ?;""",
                    args=(username,), one=False)


def get_regrade_requests():
    """Return all regrade requests"""
    return query_db("""SELECT * FROM RegradeRequests;""", (), one=False)


def isUser(username: str, password: str):
    """Return True if username is in database"""
    result = query_db("""SELECT username FROM User WHERE User.username == ?
                    AND User.password == ?;""",
                      args=(username, password,))
    if result is None:
        return False
    return True


def isInstructor(username: str):
    """Return true if username is instructor"""
    result = query_db("""SELECT username FROM User WHERE User.username == ?
                    AND User.isInstructor == 1;""",
                      args=(username,))
    if result is None:
        return False
    return True


def addUser(username: str, password: str, isInstructor: int):
    """Insert username to database"""
    update_db("""INSERT INTO User VALUES (?,?,?);""",
              args=(username, password, isInstructor,))


def addUserMarks(username: str):
    """Add username marks to database"""
    update_db("""INSERT INTO StudentMark
    VALUES (?,?,?,?,?,?,?);""", args=(username, 0, 0, 0, 0, 0, 0,))


def addFeedback(username: str, content: str):
    """Add content to database"""
    update_db("""INSERT INTO Feedback VALUES (?,?);""",
              args=(username, content,))


def addRegradeRequest(username: str, content: str):
    """Add regrade request to database"""
    update_db("""INSERT INTO RegradeRequests VALUES (?, ?);""",
              args=(username, content,))


def updateUserMarks(username: str, marks: list):
    """Update user marks"""
    update_db("""UPDATE StudentMark SET Assignment1 = ?,
    Assignment2 = ?,Assignment3 = ?
    ,Assignment4 = ?,Midterm = ?
    ,FinalTest = ? WHERE StudentMark.username == ?;""",
              args=(marks[0], marks[1],
                    marks[2], marks[3], marks[4], marks[5], username,))


app = Flask(__name__)
app.secret_key = 'cscb63'

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        # close the database if we are connected to it
        db.close()


@app.route('/')
def index():
    # return render_template('index.html')
    # addFeedback("Andy", "Very very good")
    # addRegradeRequest("Max", "want to regrade second assignment")
    # addUser("student3", "student3", 0)
    # addUserMarks("student3")
    # updateUserMarks("student3", [1, 0, 1, 0, 0, 0])
    # db = getattr(g, '_database', None)
    # if db is not None:
    # close the database if we are connected to it
    #    db.close()
    if 'username' in session:
        return render_template("index.html", Ins = isInstructor(session['username']))
    return redirect(url_for('login'))

@app.route('/announcement')
def announcement():
    return render_template('announcement.html', Ins = isInstructor(session['username']))



@app.route('/piazza')
def piazza():
    return redirect("https://piazza.com/class/kju7e2uwa8p3sf")


@app.route('/calendar')
def calendar():
    return render_template('calendar.html', Ins = isInstructor(session['username']))


@app.route('/lecture')
def lecture():
    return render_template('lecture.html', Ins = isInstructor(session['username']))


@app.route('/tutorial')
def tutorial():
    return render_template('tutorial.html', Ins = isInstructor(session['username']))


@app.route('/assignment')
def assignment():
    return render_template('assignment.html', Ins = isInstructor(session['username']))

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['password'] = request.form['password']
        if isUser(session['username'], session['password']):
            return redirect(url_for('index'))
        else:
            session.pop('username', None)
            session.pop('password', None)
            return 'User does not exist, check your password/signup to login to the course website'
    elif 'username' in session and 'password' in session:
        return redirect(url_for('index'))
    else:
        return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('password', None)
    return 'you logged out'

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'GET':
        return render_template('feedback.html', Ins = isInstructor(session['username']))
    if request.method == 'POST':
        return render_template('accept.html', Ins = isInstructor(session['username']))


if __name__ == '__main__':
    app.run(debug=True)
