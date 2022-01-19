from flask import Flask, render_template, redirect, request, url_for, session, flash
from models.Usermodel import User
from models.Databasemodel import Database
from models.Requests import Requests
from models.barter import BarterRequest
from models.barter import RequestId
from flask_mail import Mail, Message
from random import randint
from passlib.hash import sha256_crypt

application = Flask(__name__)
mail=Mail(application)

application.config['MAIL_SERVER'] = 'smtp.gmail.com'
application.config['MAIL_PORT'] = 465
application.config['MAIL_USERNAME'] = 'barter.fintech@gmail.com'
application.config['MAIL_PASSWORD'] = '**********'
application.config['MAIL_USE_SSL'] = True
mail = Mail(application)

application.secret_key='cloud'

@application.route('/')
def home_page():
    return render_template('home.html')

@application.before_first_request
def initialize_database():
    Database.initialize()

@application.route('/signup/')
def signup_page():
    return render_template('signup.html')

@application.route('/login/')
def login_page():
    session["email"]=None
    return render_template('login.html')

@application.route('/auth/details', methods=['POST'])
def registration():
    session['email']= None
    name=request.form['name']
    age=request.form['age']
    gender= request.form['gender']
    occupation=request.form['occupation']
    email=request.form['email']
    password=request.form['password']
    type_of_service=request.form['type_of_service']
    details_of_service=request.form['details_of_service']
    if User.search_for_signup(email):
        subject='FINTECH Verification OTP'
        msg=Message(subject, sender='barter.fintech@gmail.com', recipients=[email])
        val = randint(1000,9999)
        final_val=str(val)
        msg.body="OTP for your verification is: " + final_val
        mail.send(msg)
        return render_template('verifyemail.html', name=name, age=age, gender=gender, occupation=occupation, email=email, password=password, type_of_service=type_of_service, details_of_service=details_of_service, final_val=final_val)
    else:
        flash("User Already Exist, Kindly Login", "error")
        return redirect(url_for('signup_page'))

@application.route('/auth/signup', methods=['POST'])
def register():
    otp=request.form['otp']
    details=request.form['details']
    det=details.split('-')
    name=det[0]
    age=det[1]
    gender=det[2]
    occupation=det[3]
    email=det[4]
    password=det[5]
    type_of_service=det[6]
    details_of_service=det[7]
    final_val=det[8]
    services_offered=[{
                        'type_of_service':type_of_service,
                        'details_of_service':details_of_service
    }]
    if int(otp)==int(final_val):
        password1=sha256_crypt.encrypt(password)
        if User.signup_user(name, age, gender, occupation, email, password1, services_offered):
            return  redirect(url_for('profile'))
        else:
            flash('Problem signing up','error')
            return redirect(url_for('signup_page'))
    else:
        flash('You entered incorrect OTP. Try Signing up again','error')
        return redirect(url_for('signup_page'))

@application.route('/auth/login', methods=['POST'])
def login():
    if request.method=='GET':
        session['email']=None
        return redirect(url_for(login_page))
    else:
        session['email']=None
        email=request.form['email']
        password=request.form['password']

        if User.validate_login(email, password):
            User.login(email)
            return redirect(url_for('profile'))
        else:
            session['email']=None
            flash("Invalid Credentials", "error")
        return redirect(url_for('login_page'))

@application.route('/profile/')
def profile():
    if session["email"] == None:
        return redirect(url_for('login_page'))
    else:
        current_user= User.search_user(session["email"])
        return render_template('profile.html', email=session["email"], name=current_user.name, 
                                age=current_user.age, gender=current_user.gender, occupation=current_user.occupation,
                                services_offered=current_user.services_offered)

@application.route('/logout/')
def logout():
    session["email"]=None
    return redirect(url_for('home_page'))

@application.route('/addservice/')
def add_service():
    if session['email'] == None:
        return redirect(url_for('login_page'))
    else:
        return render_template('addservice.html')

@application.route('/add/ser', methods=['POST'])
def add_serv():
    type_of_service=request.form['type_of_service']
    details_of_service=request.form['details_of_service']
    new_service={
                    'type_of_service':type_of_service,
                    'details_of_service':details_of_service
    }
    email=session['email']
    if User.add_service(new_service, email):
        flash("Service Added", "error")
        return redirect(url_for('add_service'))
    else:
        flash("Error While Adding Service", "error")
        return redirect(url_for('addservice.html'))

@application.route('/requestservice/')
def request_service():
    if session["email"]== None:
        return redirect(url_for('login_page'))
    else:
        return render_template('requestservice.html')

@application.route('/auth/requests', methods=["POST"])
def service_request():
    type_of_service=request.form['type_of_service']
    details_of_service=request.form['details_of_service']
    serv_req={
                'type_of_request':type_of_service,
                'details_of_service':details_of_service,
                'email':session['email']
    }
    if Requests.request(serv_req):
        requestt={
                    'type_of_request':type_of_service,
                'details_of_service':details_of_service,
        }
        User.request_service(requestt, session['email'])
        user=User.search_user(session['email'])
        flash("Request Submitted Successfully","error")
        return render_template('servicesrequested.html', requests=user.services_requested)
    else:
        flash("Request not submitted, TRY AGAIN", "error")
        return redirect(url_for('request_service'))

@application.route('/servicesrequested/')
def view_services():
    user=User.search_user(session['email'])
    return render_template('servicesrequested.html', requests=user.services_requested)


@application.route('/deleteservice/')
def del_service():
    if session['email']== None:
        return redirect(url_for('login_page'))
    else:
        current_user=User.search_user(session['email'])
    return render_template('deleteservice.html', services_offered=current_user.services_offered)

@application.route('/auth/deleteservice', methods=["POST"])
def remove_service():
    if session['email']==None:
        return redirect(url_for('login_page'))
    else:
        delete_service=request.form['delete_service']
        user=User.search_user(session["email"])
        for service in user.services_offered:
            if service["details_of_service"] == delete_service:
                user.services_offered.remove(service)
                break
            else:
                continue
        if User.update_services_offered(session["email"], user.services_offered):
            return redirect(url_for('profile'))

@application.route('/searchservice/')
def search_service():
    if session['email']==None:
        return redirect(url_for('login_page'))
    else:
        return render_template('searchservice.html')

@application.route('/auth/search', methods=["POST"])
def look_service():
    if session['email']==None:
        return redirect(url_for('login_page'))
    else:
        search_type=request.form['search_type']
        users=User.search_users_by_service(search_type)
        if (len(users)==0) or (len(users)==1 and users[0]['email']==session['email']):
            flash("Services under this category are currently not available","error")
            return redirect(url_for('search_service'))
        else:
            return render_template('searchresults.html', users=users, type=search_type, email=session['email'])

@application.route('/auth/barterrequest', methods=["POST"])
def barter_request():
    if session['email']==None:
        return redirect(url_for('login_page'))
    else:
        barter_req=request.form['barter_request']
        req=barter_req.split("-")
        req_to=req[0]
        type_of_request=req[1]
        details=req[2]
        current_user=User.search_user(session['email'])
        number=RequestId.get_number()
        number=number+1
        if BarterRequest.barter_request(number, req_to, current_user.email, type_of_request, details, current_user.services_offered):
            RequestId.update()
            return redirect(url_for('profile'))
        else:
            flash("You have already submitted a same barter request, which is in progress", 'error')
            return redirect(url_for('search_service'))

@application.route('/barterrequestssent/', methods=['GET'])
def requests_sent():
    if session['email']==None:
        return redirect(url_for('login_page'))
    else:
        reqs=BarterRequest.get_requests_sent(session['email'])
        if len(reqs)!=0:
            return render_template('barterrequestssent.html', reqs=reqs)
        else:
            flash("You have not sent any barter requests","error")
            return redirect(url_for('profile'))

@application.route('/barterrequestsreceived/', methods=['GET'])
def requests_received():
    if session['email']==None:
        return redirect(url_for('login_page'))
    else:
        reqs=BarterRequest.get_requests_received(session['email'])
        if len(reqs)!=0:
            return render_template('barterrequestsreceived.html', reqs=reqs)
        else:
            flash("You have not received any barter requests","error")
            return redirect(url_for('profile'))

@application.route('/auth/addcomments', methods=['POST'])
def add_comments():
    details=request.form['details']
    request_number=int(details)
    new_comments=request.form['new_comments']
    add_comments=session['email']+": "+new_comments
    print(add_comments)
    if BarterRequest.add_comments(request_number, add_comments):
        return redirect(url_for('profile'))
    else:
        flash("Error while adding comments",'error')
        return redirect(url_for('requests_sent'))

@application.route('/auth/receivedcomments', methods=['POST'])
def reaction_comments():
    details=request.form['details']
    request_number=int(details)
    new_comments=request.form['new_comments']
    check=new_comments.lower()
    print(check)
    if check=='accept':
        flag=1
        add_comments=session['email']+": "+new_comments
    else:
        if check=='decline':
            flag=2
            add_comments=session['email']+": "+new_comments
        else:
            flag=0
            add_comments=session['email']+": "+new_comments
    if BarterRequest.received_comments(request_number, flag, add_comments):
        return redirect(url_for('profile'))
    else:
        flash("Error while adding comments",'error')
        return redirect(url_for('requests_received'))

@application.route('/acceptedbarterrequests/', methods=['GET'])
def accepted_requests():
    if session['email']==None:
        return redirect(url_for('login_page'))
    else:
        reqs=BarterRequest.get_requests_accepted(session['email'])
        if len(reqs)==0:
            flash('You have no accepted barter requests','error')
            return redirect(url_for('profile'))
        else:
            return render_template('acceptedbarterrequests.html',reqs=reqs)

@application.route('/declinedbarterrequests/', methods=['GET'])
def declined_requests():
    if session['email']==None:
        return redirect(url_for('login_page'))
    else:
        reqs=BarterRequest.get_requests_declined(session['email'])
        if len(reqs)==0:
            flash('You have no declined barter requests','error')
            return redirect(url_for('profile'))
        else:
            return render_template('declinedbarterrequests.html',reqs=reqs)


if __name__=="__main__":
    application.run(debug=True)