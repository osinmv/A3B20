import sqlite3
from flask import Flask, render_template, url_for, request, redirect, g, session
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


def get_instructors():
    """Return instructors"""
    return query_db("""SELECT DISTINCT * FROM User 
                    WHERE User.isInstructor == 1;""",
                    (), one=False)


def get_students():
    """Return instructors"""
    return query_db("""SELECT DISTINCT * FROM User 
                    WHERE User.isInstructor == 0;""",
                    (), one=False)


def get_feedback(username: str):
    """Return feedback by instructor"""
    return query_db("""SELECT * FROM Feedback
                    WHERE Feedback.username == ?;""",
                    args=(username,), one=False)


def get_regrade_requests(instructor: str):
    """Return all regrade requests"""
    return query_db("""SELECT * FROM RegradeRequests WHERE instructor==?;""",
                    (instructor,), one=False)


def isUser(username: str):
    """Return True if username is in database"""
    result = query_db(
        """SELECT username FROM User WHERE User.username == ?;""",
        args=(username,))
    if result is None:
        return False
    return True


def validate(username: str, password: str):
    """Return true if username and password are correct"""
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


def addFeedback(username: str, q1: str, q2: str, q3: str, q4: str):
    """Add content to database"""
    update_db("""INSERT INTO Feedback VALUES (?,?,?,?,?);""",
              args=(username, q1, q2, q3, q4,))


def addRegradeRequest(username: str, content: str, instructor: str):
    """Add regrade request to database"""
    update_db("""INSERT INTO RegradeRequests VALUES (?, ?,?);""",
              args=(username, content, instructor,))


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
        return render_template("index.html",
                               Ins=isInstructor(session['username']),
                               username=session['username'])
    return redirect(url_for('login'))


@app.route('/announcement')
def announcement():
    if 'username' in session:
        return render_template('announcement.html',
                               Ins=isInstructor(session['username']),
                               username=session['username'])
    return redirect(url_for('login'))


@app.route('/piazza')
def piazza():
    if 'username' in session:
        return redirect("https://piazza.com/class/kju7e2uwa8p3sf")
    return redirect(url_for('login'))


@app.route('/calendar')
def calendar():
    if 'username' in session:
        return render_template('calendar.html',
                               Ins=isInstructor(session['username']),
                               username=session['username'])
    return redirect(url_for('login'))


@app.route('/lecture')
def lecture():
    if 'username' in session:
        return render_template('lecture.html',
                               Ins=isInstructor(session['username']),
                               username=session['username'])
    return redirect(url_for('login'))


@app.route('/tutorial')
def tutorial():
    if 'username' in session:
        return render_template('tutorial.html',
                               Ins=isInstructor(session['username']),
                               username=session['username'])
    return redirect(url_for('login'))


@app.route('/assignment')
def assignment():
    if 'username' in session:
        return render_template('assignment.html',
                               Ins=isInstructor(session['username']),
                               username=session['username'])
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['password'] = request.form['password']
        if validate(session['username'], session['password']):
            return redirect(url_for('index'))
        else:
            session.pop('username', None)
            session.pop('password', None)
            return redirect(url_for('notExist'))
    elif 'username' in session and 'password' in session:
        return redirect(url_for('index'))
    else:
        return render_template('login.html')


@app.route('/notExist')
def notExist():
    return render_template('notExist.html')


@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        if(not isUser(request.form["username"])):
            addUser(request.form["username"], request.form["password"],
                    int(request.form["persontype"]))
            if(int(request.form["persontype"]) == 0):
                addUserMarks(request.form["username"])
            return render_template("login.html")
        else:
            return render_template('signup.html')
    else:
        return render_template('signup.html')


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if 'username' in session:
        if isInstructor(session['username']):
            return redirect(url_for('notStudent'))
        if request.method == 'GET':
            db = get_db()
            db.row_factory = make_dicts

            return render_template('feedback.html',
                                   Ins=isInstructor(session['username']),
                                   instructors=get_instructors(),
                                   username=session['username'])
        if request.method == 'POST':
            addFeedback(request.form["Instruct_name"],
                        request.form['teaching'], request.form['teachImprove'],
                        request.form['labs'], request.form['labImprove'])
            return render_template('accept.html',
                                   Ins=isInstructor(session['username']),
                                   username=session['username'])
    return redirect(url_for('login'))


@ app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('password', None)
    return render_template('logout.html')


@app.route('/studentmark')
def studentmark():
    if 'username' in session:
        if isInstructor(session['username']):
            return redirect(url_for('notStudent'))
        return render_template('studentmark.html',
                               Ins=isInstructor(session['username']),
                               marks=get_student_marks(session['username']),
                               username=session['username'])
    return redirect(url_for('login'))


@app.route('/remarkrequest', methods=['GET', 'POST'])
def remarkrequest():
    if 'username' in session:
        if isInstructor(session['username']):
            return redirect(url_for('notStudent'))
        if request.method == 'GET':
            db = get_db()
            db.row_factory = make_dicts
            return render_template('remarkrequesta1.html',
                                   variable='test',
                                   instructors=get_instructors(),
                                   Ins=isInstructor(session['username']),
                                   username=session['username'])

        if request.method == 'POST':
            addRegradeRequest(
                session['username'], "A1. "+request.form['message'],
                request.form["Instruct_name"])
            return render_template('sentremark.html',
                                   Ins=isInstructor(session['username']),
                                   username=session['username'])
    return redirect(url_for('login'))


@app.route('/remarkrequesta2', methods=['GET', 'POST'])
def remarkrequesta2():
    if 'username' in session:
        if isInstructor(session['username']):
            return redirect(url_for('notStudent'))
        if request.method == 'GET':
            db = get_db()
            db.row_factory = make_dicts
            return render_template('remarkrequesta2.html',
                                   variable='test',
                                   instructors=get_instructors(),
                                   Ins=isInstructor(session['username']))

        if request.method == 'POST':
            addRegradeRequest(
                session['username'], "A2. "+request.form['message'],
                request.form["Instruct_name"])
            return render_template('sentremark.html',
                                   Ins=isInstructor(session['username']))
    return redirect(url_for('login'))


@app.route('/remarkrequesta3', methods=['GET', 'POST'])
def remarkrequesta3():
    if 'username' in session:
        if isInstructor(session['username']):
            return redirect(url_for('notStudent'))
        if request.method == 'GET':
            db = get_db()
            db.row_factory = make_dicts
            return render_template('remarkrequesta3.html',
                                   variable='test',
                                   instructors=get_instructors(),
                                   Ins=isInstructor(session['username']))

        if request.method == 'POST':
            addRegradeRequest(
                session['username'], "A3. "+request.form['message'],
                request.form["Instruct_name"])
            return render_template('sentremark.html',
                                   Ins=isInstructor(session['username']))
    return redirect(url_for('login'))


@app.route('/remarkrequesta4', methods=['GET', 'POST'])
def remarkrequesta4():
    if 'username' in session:
        if isInstructor(session['username']):
            return redirect(url_for('notStudent'))
        if request.method == 'GET':
            db = get_db()
            db.row_factory = make_dicts
            return render_template('remarkrequesta4.html',
                                   variable='test',
                                   instructors=get_instructors(),
                                   Ins=isInstructor(session['username']))

        if request.method == 'POST':
            addRegradeRequest(
                session['username'], "A4. "+request.form['message'],
                request.form["Instruct_name"])
            return render_template('sentremark.html',
                                   Ins=isInstructor(session['username']))
    return redirect(url_for('login'))


@app.route('/remarkrequestmidterm', methods=['GET', 'POST'])
def remarkrequestmidterm():
    if 'username' in session:
        if isInstructor(session['username']):
            return redirect(url_for('notStudent'))
        if request.method == 'GET':
            db = get_db()
            db.row_factory = make_dicts
            return render_template('remarkrequestmidterm.html',
                                   variable='test',
                                   instructors=get_instructors(),
                                   Ins=isInstructor(session['username']))

        if request.method == 'POST':
            addRegradeRequest(session['username'],
                              "Midterm. "+request.form['message'],
                              request.form["Instruct_name"])
            return render_template('sentremark.html',
                                   Ins=isInstructor(session['username']))
    return redirect(url_for('login'))


@app.route('/remarkrequestfinal', methods=['GET', 'POST'])
def remarkrequestfinal():
    if 'username' in session:
        if isInstructor(session['username']):
            return redirect(url_for('notStudent'))
        if request.method == 'GET':
            db = get_db()
            db.row_factory = make_dicts
            return render_template('remarkrequestfinal.html',
                                   variable='test',
                                   instructors=get_instructors(),
                                   Ins=isInstructor(session['username']))

        if request.method == 'POST':
            addRegradeRequest(session['username'],
                              "Final. "+request.form['message'],
                              request.form["Instruct_name"])
            return render_template('sentremark.html',
                                   Ins=isInstructor(session['username']))
    return redirect(url_for('login'))


@app.route('/showAllGrade')
def showAllGrade():
    if 'username' in session:
        if not isInstructor(session['username']):
            return redirect(url_for('notIns'))
        db = get_db()
        db.row_factory = make_dicts

        username = session['username']
        Ins = isInstructor(session['username'])
        grades = []
        for grade in get_all_marks():
            grades.append(grade)

        db.close()
        return render_template('showAllGrade.html', grade=grades,
                               username=username, Ins=Ins)
    return redirect(url_for('login'))


@app.route('/checkFeedback')
def checkFeedback():
    if 'username' in session:
        if not isInstructor(session['username']):
            return redirect(url_for('notIns'))
        db = get_db()
        db.row_factory = make_dicts

        username = session['username']
        Ins = isInstructor(session['username'])
        feedbacks = []
        for feedback in get_feedback(session['username']):
            feedbacks.append(feedback)

        db.close()
        return render_template('checkFeedback.html',
                               feedback=feedbacks, username=username, Ins=Ins)
    return redirect(url_for('login'))


@app.route('/checkRegrade')
def checkRegrade():
    if 'username' in session:
        if not isInstructor(session['username']):
            return redirect(url_for('notIns'))
        db = get_db()
        db.row_factory = make_dicts

        username = session['username']
        Ins = isInstructor(session['username'])
        requests = []
        for request in get_regrade_requests(session['username']):
            requests.append(request)

        db.close()
        return render_template('checkRegrade.html', request=requests,
                               username=username, Ins=Ins)
    return redirect(url_for('login'))


@app.route('/chooseStudent', methods=['GET', 'POST'])
def chooseStudent():
    if 'student_name' in session:
        session.pop('student_name', None)

    if 'username' in session:
        if not isInstructor(session['username']):
            return redirect(url_for('notIns'))
        if request.method == 'GET':
            db = get_db()
            db.row_factory = make_dicts

            username = session['username']
            Ins = isInstructor(session['username'])
            students = []
            for student in get_students():
                students.append(student)

            db.close()
            return render_template('chooseStudent.html', student=students,
                                   username=username, Ins=Ins)
        else:
            session['student_name'] = request.form['student_name']
            return redirect(url_for('editMark'))
    return redirect(url_for('login'))


@app.route('/editMark', methods=['GET', 'POST'])
def editMark():
    if 'student_name' not in session:
        return redirect(url_for('chooseStudent'))
    if 'username' in session:
        if not isInstructor(session['username']):
            return redirect(url_for('notIns'))
        if request.method == 'GET':
            db = get_db()
            db.row_factory = make_dicts
            mark = get_student_marks(session['student_name'])

            username = session['username']
            Ins = isInstructor(session['username'])

            db.close()
            return render_template('editMark.html',
                                   student=session['student_name'], mark=mark,
                                   username=username, Ins=Ins)
        else:
            newMark = [request.form['newA1'], request.form['newA2'],
                       request.form['newA3'],
                       request.form['newA4'], request.form['newMid'],
                       request.form['newFinal']]
            updateUserMarks(session['student_name'], newMark)
            session.pop('student_name', None)
            return render_template('assigned.html')
    return redirect(url_for('login'))


@app.route('/notIns')
def notIns():
    if 'username' in session:
        if isInstructor(session['username']):
            return redirect(url_for('notStudent'))
        return render_template('notIns.html')
    return redirect(url_for('login'))


@app.route('/notStudent')
def notStudent():
    if 'username' in session:
        if not isInstructor(session['username']):
            return redirect(url_for('notIns'))
        return render_template('notStudent.html')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
