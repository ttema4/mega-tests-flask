from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = '1423'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tests.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Qwe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, nullable=False)
    question = db.Column(db.String, nullable=False)
    var = db.Column(db.String, nullable=False)
    ans = db.Column(db.String, nullable=False)
    autor = db.Column(db.String, nullable=False)

    def get_id(self):
        return self.test_id

    def get_qwe(self):
        return self.question

    def get_var(self):
        return self.var

    def get_ans(self):
        return self.ans


class Res(db.Model):
    test_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    percent = db.Column(db.String, nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    un = db.Column(db.String, nullable=False)
    pw = db.Column(db.String, nullable=False)
    mail = db.Column(db.String, nullable=False)

    def __str__(self):
        return str(self.id) + ' ' + self.un + ' ' + self.pw + ' ' + self.mail


@app.route('/register', methods=['GET', 'POST'])
def registerpage():
    if str(session.get('un', '')) != '':
        return render_template('nreg.html')
    else:
        if request.method == 'GET':
            return render_template("register.html", warning='')
        elif request.method == "POST":
            data = request.form.to_dict()
            un = data['login']
            pw = data['password']
            mail = data['mail']
            logged = False
            for user in User.query.all():
                if str(user).split()[1] == un:
                    logged = True
                    break
            if not logged:
                user = User(un=un, pw=pw, mail=mail)
                try:
                    db.session.add(user)
                    db.session.commit()
                    return redirect('/login')
                except:
                    return 'Ошибка'
            else:
                return render_template('register.html', warning='Такой пользователь есть.')


@app.route('/login', methods=['GET', 'POST'])
def loginpage():
    if str(session.get('un', '')) != '':
        return render_template('nlog.html')
    else:
        if request.method == 'GET':
            return render_template('login.html', warning='')
        elif request.method == 'POST':
            data = request.form.to_dict()
            un = data['login']
            pw = data['password']
            name = False
            pas = False
            for user in User.query.all():
                if str(user).split()[1] == un:
                    name = True
                    if str(user).split()[2] == pw:
                        pas = True
                        session['mail'] = str(user).split()[3]
                        break
            if name and pas:
                session['un'] = un
                return redirect('/profile')
            elif name and (not pas):
                return render_template('login.html', warning='Неверный пароль.')
            else:
                return render_template('login.html', warning='Такого пользователя не существует.')


@app.route('/profile', methods=["GET", "POST"])
def profile():
    if request.method == 'GET':
        if str(session.get('un', '')) != '' and str(session.get('un', '')) is not None:
            return render_template('profile.html', un=str(session.get('un', '')), email=str(session.get('mail', '')))
        else:
            return render_template('nprofile.html')
    else:
        session.pop('mail', None)
        session.pop('un', None)
        return render_template('nprofile.html')


@app.route('/pass-test', methods=['GET', 'POST'])
def pass_test():
    if request.method == 'GET':
        session['qwe'] = 0
        session['cor'] = 0
        session['all'] = 0
        session['rd'] = False
        tests = []
        for test in Qwe.query.all():
            if test.get_id() == int(session['test']):
                tests.append(test)
        if len(tests) == 0:
            return render_template('error.html')
        else:
            return render_template('passtest.html', qwe=tests[session['qwe']].get_qwe(),
                                   vars=tests[session['qwe']].get_var(),
                                   ln=len(tests[session['qwe']].get_var().split(';')))
    else:
        an = request.form.get('corr')
        session['all'] += 1
        session['qwe'] += 1
        tests = []
        for test in Qwe.query.all():
            if test.get_id() == int(session['test']):
                tests.append(test)
        if an == str(tests[session['qwe'] - 1].get_ans()):
            session['cor'] += 1
        if len(tests) == session['qwe']:
            return render_template('final.html', right=session['cor'], all=session['all'])
        else:
            return render_template('passtest.html', qwe=tests[session['qwe']].get_qwe(),
                                   vars=tests[session['qwe']].get_var(),
                                   ln=len(tests[session['qwe']].get_var().split(';')))


@app.route('/create-test', methods=['GET', 'POST'])
def make_test():
    if str(session.get('un', '')) == '':
        return render_template('nprofile.html')
    else:
        if request.method == 'GET':
            session['test_id'] = 1
            for test in Qwe.query.all():
                if session['test_id'] < test.get_id() + 1:
                    session['test_id'] = test.get_id() + 1
            return render_template('maketest.html')
        elif request.method == 'POST':
            data = request.form.to_dict()
            qw = data['qw']
            ans1 = data['ans1']
            ans2 = data['ans2']
            ans3 = data['ans3']
            ans4 = data['ans4']
            ans = [el for el in [ans1, ans2, ans3, ans4] if el != '']
            corr = request.form.get('corr')

            qwe = Qwe(test_id=session['test_id'], question=qw, var=';'.join(ans), ans=corr, autor=session['un'])
            try:
                db.session.add(qwe)
                db.session.commit()
                return render_template('maketest.html')
            except:
                return 'Ошибка'


@app.route('/test-done', methods=['GET', 'POST'])
def testdone():
    return render_template('done.html', numb=session['test_id'])


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('homepage.html')
    elif request.method == 'POST':
        session['test'] = request.form.get('inputPassword2')
        return redirect('/pass-test')


def main():
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
