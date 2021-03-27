from flask import Flask, render_template, url_for, request, redirect

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/announcement')
def announcement():
    return render_template('announcement.html')

@app.route('/piazza')
def piazza():
    return redirect("https://piazza.com/class/kju7e2uwa8p3sf")

@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

@app.route('/lecture')
def lecture():
    return render_template('lecture.html')

@app.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')

@app.route('/assignment')
def assignment():
    return render_template('assignment.html')

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'GET':
        return render_template('feedback.html')
    if request.method == 'POST':
        return render_template('accept.html')

if __name__ == '__main__':
    app.run(debug=True)