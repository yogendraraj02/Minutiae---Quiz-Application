from flask import  Flask,request,redirect,render_template,url_for,session,flash
import requests


from apiques import quizapi

from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,login_user,logout_user,login_required,current_user,LoginManager

from flask_admin import  Admin
app = Flask(__name__)
admin = Admin(app)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'











db = SQLAlchemy(app)
class Questions(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    question = db.Column(db.String(1000),nullable=False)
    option1= db.Column(db.String(250),nullable=False)
    option2 = db.Column(db.String(250), nullable=False)
    option3 = db.Column(db.String(250), nullable=False)
    option4 = db.Column(db.String(250),nullable=False)
    # option4 = db.Column(db.String(250), nullable=False)
    answer = db.Column(db.String(250),nullable=False)
    author = db.Column(db.String(500),nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    #country = db.Column(db.String(1000))
    #questions = relationship("Questions", back_populates="")
    responses = db.Column(db.JSON)

from flask_admin.contrib.sqla import ModelView
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Questions, db.session))













#db.create_all()

# def fun():
#     new_user = User(
#
#         email="yo@a.com",
#         name="yo",
#
#         password="1234",
#         responses = {"akshay":[100]},
#     )
#     db.session.add(new_user)
#     db.session.commit()
# def read():
#     user = User.query.filter_by(name="yo").first()
#     user.responses["akki"] = 10
#     print(user.responses)
# #fun()
# read()
############################################################
#login#
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():

    return render_template("index.html",logged_in=current_user.is_authenticated)

@app.route("/signup",methods=["POST","GET"])
def signup():
    if request.method=="POST":


        if User.query.filter_by(email=request.form.get('email')).first():
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(

            email=request.form.get('email'),
            name=request.form.get('name'),

            password=hash_and_salted_password,


        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("home"))

    return render_template("signup.html", logged_in=current_user.is_authenticated)



@app.route("/login",methods=["POST","GET"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))

    return render_template("login.html", logged_in=current_user.is_authenticated)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/profile")
@login_required
def user():
    name = current_user.name

    user = User.query.filter_by(name=name).first()
    print(user.email)
    print(user.password)
    return render_template("profile.html",user=user,logged_in=current_user.is_authenticated)


@app.route("/user_questions")
@login_required
def user_questions():
    questions = Questions.query.filter_by(author=current_user.name).all()
    return render_template("user_questions.html",name = current_user.name.upper(),questions=questions,logged_in=current_user.is_authenticated)



















''' 
Quiz Maker
'''

@app.route("/makequiz")
@login_required
def make_quiz():
    return render_template("quizmaker.html",logged_in=current_user.is_authenticated)



@app.route('/addquestion',methods=["POST","GET"])
@login_required
def addquestion():
    if request.method =="POST":

        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        answer = request.form['answer']
        question = request.form['question']

        new_question = Questions(author = current_user.name,question=question,option1=option1,option2=option2,option3=option3,option4 = option4,answer=answer)
        db.session.add(new_question)
        db.session.commit()
        return redirect(url_for('addquestion'))

    return redirect(url_for('home'))


@app.route("/show_quiz",methods=["POST","GET"])
@login_required
def show_quiz():
    if request.method=="GET":

        questions = db.session.query(Questions).all()
        secs = len(questions)*15
        time_until = timer(0,secs)
        print("In show quiz:",timeuntil)
        #questions = Questions.query.paginate(per_page=1,page=page_num,error_out=True)

        return render_template("custom_quiz.html",question=questions,logged_in=current_user.is_authenticated,time_until=time_until)

import smtplib
from _datetime import datetime

@app.route("/show_result/<code>",methods=["POST"])
@login_required
def show_result(code):



    score = 0

    correct_answers = []
    incorrect_answers = []
    if request.method =="POST":
        questions = Questions.query.filter_by(author=code).all()
        for ques in questions:
            try:

                ans_got = request.form[str(ques.id)]
            except KeyError:
                continue
            #print(ans_got)
            if ans_got == ques.answer:
                correct_answers.append(ans_got)
                score +=1
                #print("correct_answers:",correct_answers)
            else:
                incorrect_answers.append(ans_got)
                #print("Incorrect_answers:", incorrect_answers)
            # with smtplib.SMTP("smtp.gmail.com") as connection:
            #     connection.starttls()
            #     connection.login(MY_EMAIL, MY_PASSWORD)
            #     connection.sendmail(
            #         from_addr=MY_EMAIL,
            #         to_addrs=current_user.email,
            #         msg=f"Subject:Your Score Minutae Quiz! \n\nScore :{score}\n"
            #     )
        #for response save
        quizmakeruser= User.query.filter_by(name=code).first()


        data = {current_user.name:score*10}
        quizmakeruser.responses = data
        db.session.commit()
        print(quizmakeruser.responses)

        with open(f"USER RESPONSES/{code}responses.txt",mode='a') as file:
            file.write(current_user.name+"="+str(score*10)+"\n")

        return render_template("score_api.html",logged_in=current_user.is_authenticated,score= score,incorrect_answers=incorrect_answers,correct_answers=correct_answers,total_questions=len(questions))
    #return redirect("index.html")


@app.route('/saveresult',methods=["POST","GET"])
@login_required
def saveresult():
    #print(all_questions)
    #print(questions_set, options_set)
    if request.method=="POST":
        answ = ""
        for ques in all_questions:
            answ = request.form[ques["question"]]
            #print(answ)
        return f"answers from form:{answ}"
    return "Get called"

#############################################################################

@app.route('/quizapi',methods=["POST","GET"])
@login_required
def quiz_api():
    if request.method == "POST":
        category = request.form["category"]
        amt = request.form["amount"]

        difficulty = request.form["difficulty"]
        #print(amt,category,difficulty)
        questions = quizapi(amt,category,difficulty)


        with open("correct_answers.txt",mode="w") as f:

            for ques in questions:
                f.write(ques["correct_answer"]+"\n")

        #print(questions)
        time_until = timer(0,int(amt)*15)
        return render_template('quizapi.html',questions = questions,logged_in=current_user.is_authenticated,time_until=time_until)
    else:
        return render_template("getquizapi.html",logged_in=current_user.is_authenticated)

@app.route('/score',methods=["GET","POST"])
@login_required
def score():
    print("currentusermail:",current_user.email)
    score = 0
    user_correct_answers = []
    user_incorrect_answers = []
    with open("correct_answers.txt") as f:
        question_lines = f.readlines()
    id = 0
    for line in question_lines:
        try:
            option = request.form["ques" + str(id + 1)]
        except KeyError:
            id = id + 1
            continue
        # print("opt:",option)
        # print("line:",line)
        if option == line.rstrip("\n"):
            user_correct_answers.append(line)
            score = score + 1

        else:
            user_incorrect_answers.append(option)
        id = id + 1
        # with smtplib.SMTP("smtp.gmail.com") as connection:
        #         connection.starttls()
        #         connection.login(MY_EMAIL, MY_PASSWORD)
        #         connection.sendmail(
        #             from_addr=MY_EMAIL,
        #             to_addrs=current_user.email,
        #             msg=f"Subject:Your Score <h1>Minutae Quiz</h1>! Score :{score}\n"
        #         )
    return render_template("score_api.html",user=current_user.name,total_questions=len(question_lines),correct_answers=user_correct_answers,incorrect_answers= user_incorrect_answers,score =score,logged_in=current_user.is_authenticated)
    #return redirect("home.html")


################################################################################################



@app.route("/code",methods=["POST","GET"])
@login_required
def code():
    if request.method == 'POST':
        code = request.form["code"]
        questions = Questions.query.filter_by(author=code).all()
        time_until = timer(0,len(questions)*15)
        return render_template("quiz.html",time_until=time_until,code = code,questions = questions,logged_in=current_user.is_authenticated)

    #return render_template("code.html",logged_in=current_user.is_authenticated)



@app.route("/user_responses",methods=["POST","GET"])
@login_required
def user_responses():
    # user = User.query.filter_by(name=current_user.name).first()
    # user_r_keys = user.responses.keys()
    # user_r_vals = user.responses.values()
    # return render_template("userresponses.html",logged_in=current_user.is_authenticated,user_score = user_r_vals,user_r_names=user_r_keys)
    #with open()
    name = current_user.name
    users = []
    scores = []
    with open(f"USER RESPONSES/{name}responses.txt",mode="r") as file:
        lines =  file.readlines()
        for line in lines:
            line = line.split("=")
            users.append(line[0])
            scores.append(line[1].strip("\n"))
        #print(users)
        #print(scores)
        name = current_user.name.upper()
    return render_template("userresponses.html",name=name,logged_in=current_user.is_authenticated,users=users,scores=scores,size=len(users))



@app.route('/deletequestion/<int:id>',methods=["POST","GET"])
def deletequestion(id):

    quest = Questions.query.filter_by(id=id).first()
    print(quest)
    db.session.delete(quest)
    db.session.commit()
    return redirect(url_for("user_questions"))



####extra works........
@app.route('/timer')
def timerpage():
    #time_until = timer()
    return render_template("timer.html")

import datetime
#@app.route('/timer')
def timer(minutes,sec):
    current_time = datetime.datetime.now()
    time_until = current_time + datetime.timedelta(seconds=sec,minutes=minutes,)
    print(current_time)
    #print(time_until)
    year = time_until.year
    day = time_until.day
    month = time_until.month
    #print(year,day,month)
    fulldate = datetime.datetime(year,month,day)
    month = fulldate.strftime("%B")
    #print(month)
    fulltime = time_until.time()
    hours = fulltime.hour
    mins = fulltime.minute
    secs = fulltime.second
    #print(hours,mins,secs)
    final_time = f"{month} {day}, {year} {hours}:{mins}:{secs}"
    #print(final_time)
    return final_time
    #return render_template("timer.html",current_time=current_time,time_until=final_time)
#("Jan 5, 2022 15:37:25")
#timer()

if __name__=="__main__":
    app.run(debug=True)




