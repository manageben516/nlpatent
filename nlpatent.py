from flask import Flask, request, render_template, url_for, make_response, jsonify, send_from_directory
from flask_mail import Mail, Message
from datetime import datetime
import jwt, codecs, os, shutil
import run, OA_101_classify, generate_summary
import stripe
import sentry_sdk
from gen_const import DIR, BANK_ACCOUNT, COST_ACTIVATION, MAX_PROJECTS, MAX_PRIOR_ART, MAX_PRIOR_ARTX, MAX_KEY_ELEMENTS, MAX_KNOWN_PRIOR_ART, MAX_TRIAL_SEARCHES, MIN_PERCENT_101, CPC_SUBCLASSES_101, CPC_SECTIONS, CLIENTS, CLIENTS_TAX_RATES, CLIENTS_CURRENCY, CLIENTS_COST_SEARCH, CLIENTS_COST_UPDATE, CLIENTS_INVOICING, CLIENTS_SUBSCRIPTION, REMOVE_FILENAMES_1, REMOVE_FILENAMES_2
from gen_const import generate_daystamp, generate_timestamp, get_forward_daystamp, get_mongo_db, generate_random_password, get_list, safe_remove, safe_remove_all

sentry_sdk.init("https://cc0ca36cee0d4b12b10e0d264a764a56@sentry.io/1452573")

app = Flask(__name__)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

app.config['MAIL_SERVER'] = 'smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'stephanie@legali.city'
app.config['MAIL_PASSWORD'] = os.environ["EMAIL_PASSWORD"]
app.config['MAIL_DEFAULT_SENDER'] = 'stephanie@legali.city'

mail = Mail(app)

JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"] # for regular authentication
JWT_CLIENT_KEY = os.environ["JWT_CLIENT_KEY"] # for new client order form
JWT_PASSWORD_RESET_KEY = os.environ["JWT_PASSWORD_RESET_KEY"] # for resetting your password

STRIPE_KEYS = {
  'secret_key': os.environ["STRIPE_SECRET_KEY"],
  'publishable_key': os.environ["STRIPE_PUBLISHABLE_KEY"]
}
stripe.api_key = STRIPE_KEYS['secret_key']

##### HELPERS #####

def plan_expired(c_id):
    # get current daystamp, 'YYYY-MM-DD'
    c = generate_daystamp()
    # get client's plan's expiry daystamp
    e = get_client_expiry(c_id)
    # check if client's plan has plan_expired
    return datetime.strptime(c, '%Y-%m-%d') > datetime.strptime(e, '%Y-%m-%d')

def get_client_expiry(c_id):
    with codecs.open('{}/clients/{}/expiry.txt'.format(DIR, c_id), 'r', 'utf-8') as f:
            temp = f.read()
    return temp.strip()

def get_client_usage(c_id, usersDB):
    usage = 0
    for u in usersDB.find({"client": c_id}):
        usage += u['num_searches']*CLIENTS_COST_SEARCH[c_id] + u['num_updates']*CLIENTS_COST_UPDATE[c_id]
    return usage

def get_client_searches(c_id, usersDB):
    return sum([u['num_searches'] for u in usersDB.find({"client": c_id})])

def get_payment_info(customer_id):
    customer = stripe.Customer.retrieve(customer_id)
    card = customer.sources.retrieve(customer.default_source)
    pm = card.funding.upper()
    b = card.brand if 'brand' in card else ''
    return b, '****{}'.format(card.last4), '{}/{}'.format('%02d' % card.exp_month, str(card.exp_year))

def add_normal_user(usersDB, email, password, cl, admin, ci):
    newUser = {'email': email, 'password': password, 'first_name': email[:email.index('@')], 'last_name': '', 'num_searches': 0,
               'num_updates': 0, 'projects': [], 'country': '', 'region': '', 'client': cl, 'role': '', 'admin': admin}
    if admin and ci: newUser['stripe_id'] = ci
    usersDB.insert_one(newUser)

def send_new_user_credentials(email, password, organization, admin):
    bod = '<p>Hello,</p>'
    bod += '<p>A new NLPatent account was automatically created for you on behalf of <b>{}</b>.</p>'.format(organization)
    bod += '<p><a href="https://www.nlpatent.com">NLPatent</a> is an online patent search & analysis tool powered by the latest AI.</p>'
    bod += "<p>Here are your login credentials:</p>"
    bod += "<p><u>Username</u>: {}</p>".format(email)
    bod += "<p><u>Password</u>: {}</p>".format(password)
    if admin:
        bod += "<p>You also have administrator status, which means you can view the payment method, current usage, and a list of all the user accounts for your client organization.</p>"
    bod += "<p>If you ever have any questions or comments about the product please let us know!</p>"
    bod += '<br>Best regards,<br>Stephanie<br>COO, Legalicity'
    msg = Message("New Account Created | NLPatent", \
    sender=("Legalicity Team", "stephanie@legali.city"), \
    html=bod, \
    recipients=[email])
    mail.send(msg)

def send_results(c_id, email, project_name, file_name):
    # send a confirmation email to the user
    bod = '<p>Dear NLPatent User,</p>'
    bod += '<p>Please find attached the results of your prior art search for the following project:</p>'
    bod += "<p><b>{}</b></p>".format(project_name)
    bod += "<p>Thank you again for using our product. If you ever have any questions or comments, please let us know!</p>"
    bod += '<br>Best regards,<br>Stephanie<br>COO, Legalicity'
    msg = Message("Prior Art Search Results | NLPatent", \
    sender=("Legalicity Team", "stephanie@legali.city"), \
    html=bod, \
    recipients=[email])
    with app.open_resource('{}/clients/{}/{}/{}/{}'.format(DIR, c_id, email, project_name, file_name)) as fp:
        msg.attach(file_name, "application/vnd.openxmlformats-officedocument.wordprocessingml.document", fp.read())
    mail.send(msg)

##### ROUTES #####

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/getstarted", methods=['GET'])
def get_started():
    return send_from_directory(directory=DIR + '/static/public', as_attachment=True, filename='NLPatent - Getting Started.pdf', attachment_filename='NLPatent - Getting Started.pdf')

@app.route("/terms", methods=['GET'])
def terms():
    return send_from_directory(directory=DIR + '/static/public', as_attachment=True, filename='Legalicity - Terms of Service.pdf', attachment_filename='Legalicity - Terms of Service.pdf')

@app.route("/privacy", methods=['GET'])
def privacy():
    return send_from_directory(directory=DIR + '/static/public', as_attachment=True, filename='Legalicity - Privacy Policy.pdf', attachment_filename='Legalicity - Privacy Policy.pdf')

@app.route("/app")
def app_main():
    return render_template('app.html')

@app.route("/appdev")
def app_dev():
    return render_template('appdev.html')

@app.route("/login", methods=['POST'])
def login():
    # check if there's an email & pass (happens after a login attempt)
    if 'email' in request.form and 'password' in request.form:
        userEmail = request.form['email'].lower() # grab the entered email
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        # check if this user doesn't exist in our database
        if u == None:
            return jsonify(ERROR="The email you entered is not in our database.")
        # check if this user's password doesn't match the one we have stored
        elif u['password'] != request.form['password']:
            return jsonify(ERROR="The password you entered is incorrect.")
        else: # if we found a match, i.e. possibly successful login
            # if login successful, generate a JWT token
            token = jwt.encode({'email': userEmail}, JWT_SECRET_KEY, algorithm='HS256')
            resp = make_response(jsonify(SUCCESS="Logged in."))
            resp.set_cookie('LegalicityCookie', token, secure=True, max_age=43200) # cookie expires after 12 hours!
            return resp
    else:
        return jsonify(ERROR="Please enter the required credentials.")

@app.route("/logout")
def logout():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        resp = make_response(jsonify(SUCCESS="Logged out."))
        resp.set_cookie('LegalicityCookie', '', secure=True, expires=0) # set cookie to empty when user logs out
        return resp
    else:
        return jsonify(ERROR="You are already logged out.")

@app.route("/getprofileinfo", methods=['GET'])
def get_profile_info():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        a = 1 if u['admin'] == True else 0
        if a == 1 and 'stripe_id' in u:
            b, n, e = get_payment_info(u['stripe_id'])
            s = STRIPE_KEYS['publishable_key']
        else:
            b, n, e = None, None, None
            s = None
        return jsonify(email=userEmail, first_name=u['first_name'], last_name=u['last_name'], organization=CLIENTS[u['client']], stripe_key=s, \
        client=u['client'], role=u['role'], country=u['country'], region=u['region'], admin=a, search_cost=CLIENTS_COST_SEARCH[u['client']], \
        update_cost=CLIENTS_COST_UPDATE[u['client']], payment_method=b, payment_number=n, payment_expiry=e)
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/getcurrentproject", methods=['GET'])
def get_current_project():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # first, check if there are no projects
        if u['projects'] == []:
            return jsonify(name=None, last_edited=None, progress=None, secure=None)
        # then, get the name of the first/current project
        p_n = u['projects'][0]
        # get the user's client ID
        c_id = u['client']
        # get the project's last edited timestamp
        with codecs.open('{}/clients/{}/{}/{}/last_edited.txt'.format(DIR, c_id, userEmail, p_n), 'r', 'utf-8') as f:
            p_l = f.read()
        # get the project's progress
        if os.path.exists('{}/clients/{}/{}/{}/101_high_tech.txt'.format(DIR, c_id, userEmail, p_n)) or os.path.exists('{}/clients/{}/{}/{}/101_life_sciences.txt'.format(DIR, c_id, userEmail, p_n)):
            p_r = 4
        elif os.path.exists('{}/clients/{}/{}/{}/prior_art_results.txt'.format(DIR, c_id, userEmail, p_n)) or (os.path.exists('{}/clients/{}/{}/{}/prior_art_saved.txt'.format(DIR, c_id, userEmail, p_n)) and os.stat('{}/clients/{}/{}/{}/prior_art_saved.txt'.format(DIR, c_id, userEmail, p_n)).st_size != 0):
            p_r = 3
        elif os.path.exists('{}/clients/{}/{}/{}/input_subclasses.txt'.format(DIR, c_id, userEmail, p_n)):
            p_r = 2
        else:
            p_r = 1
        # get the project's security level
        with codecs.open('{}/clients/{}/{}/{}/secure.txt'.format(DIR, c_id, userEmail, p_n), 'r', 'utf-8') as f:
            p_s = f.read()
        # get the project's number of searches
        with codecs.open('{}/clients/{}/{}/{}/#_searches.txt'.format(DIR, c_id, userEmail, p_n), 'r', 'utf-8') as f:
            n_s = f.read()
        # get the project's number of updates
        with codecs.open('{}/clients/{}/{}/{}/#_updates.txt'.format(DIR, c_id, userEmail, p_n), 'r', 'utf-8') as f:
            n_u = f.read()
        return jsonify(name=p_n, last_edited=p_l.strip(), progress=p_r, secure=int(p_s.strip()), num_searches=int(n_s.strip()), num_updates=int(n_u.strip()))
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/getallprojects", methods=['GET'])
def get_all_projects():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # first, check if there are no projects
        if u['projects'] == []:
            return jsonify(projects=None)
        # get the user's client ID
        c_id = u['client']
        # get all projects
        p_list = []
        for p_n in u['projects']:
            # get the project's last edited timestamp
            with codecs.open('{}/clients/{}/{}/{}/last_edited.txt'.format(DIR, c_id, userEmail, p_n), 'r', 'utf-8') as f:
                p_l = f.read()
            # get the project's security level
            with codecs.open('{}/clients/{}/{}/{}/secure.txt'.format(DIR, c_id, userEmail, p_n), 'r', 'utf-8') as f:
                p_s = f.read()
            # get the project's number of searches
            with codecs.open('{}/clients/{}/{}/{}/#_searches.txt'.format(DIR, c_id, userEmail, p_n), 'r', 'utf-8') as f:
                n_s = f.read()
            # get the project's number of updates
            with codecs.open('{}/clients/{}/{}/{}/#_updates.txt'.format(DIR, c_id, userEmail, p_n), 'r', 'utf-8') as f:
                n_u = f.read()
            p_list.append({'name': p_n, 'last_edited': p_l.strip(), 'secure': int(p_s.strip()), 'num_searches': int(n_s.strip()), 'num_updates': int(n_u.strip())})
        return jsonify(projects=p_list)
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/addproject", methods=['POST'])
def add_project():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a project name
        if 'project_name' not in request.form:
            return jsonify(ERROR="Please enter the project name.")
        # check if a project with that name already exists
        if request.form['project_name'] in u['projects']:
            return jsonify(EXISTS="A project with that name already exists.")
        # check if the user reached a maximum allowed number of projects
        if len(u['projects']) >= MAX_PROJECTS:
            return jsonify(EXISTS="You cannot have more than 100 projects.")
        # get the user's client ID
        c_id = u['client']
        # generate a timestamp
        p_l = generate_timestamp()
        # check if there is a previous project & edit its timestamp
        if u['projects'] != []:
            p_n = u['projects'][0]
            with codecs.open('{}/clients/{}/{}/{}/last_edited.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f:
                f.write(p_l)
        # add the new project name to MongoDB
        p_n = request.form['project_name']
        if '/' in p_n:
            return jsonify(EXISTS="Please omit the slash ('/') from your project name.")
        p_list_updated = [p_n] + u['projects']
        usersDB.update({'email': userEmail}, {'$set': {'projects': p_list_updated}})
        # add the new project to the server: create a folder & add last_edited, secure, saved & deleted prior art (empty at first)
        try:
            os.mkdir('{}/clients/{}/{}/{}/'.format(DIR, c_id, userEmail, p_n))
        except:
            pass
        with codecs.open('{}/clients/{}/{}/{}/last_edited.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f:
            f.write(p_l)
        with codecs.open('{}/clients/{}/{}/{}/secure.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f:
            f.write("0")
        with codecs.open('{}/clients/{}/{}/{}/#_searches.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f:
            f.write("0")
        with codecs.open('{}/clients/{}/{}/{}/#_updates.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f:
            f.write("0")
        with codecs.open('{}/clients/{}/{}/{}/prior_art_saved.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f:
            f.write("")
        with codecs.open('{}/clients/{}/{}/{}/prior_art_deleted.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f:
            f.write("")
        # log it
        with codecs.open('{}/clients/{}/{}/log.txt'.format(DIR, c_id, userEmail), 'a', 'utf-8') as f:
            f.write('{} P\n'.format(p_l))
        return jsonify(SUCCESS="Project was added.")
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/removeproject", methods=['POST'])
def remove_project():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a project name
        if 'project_name' not in request.form:
            return jsonify(ERROR="Please enter the project name.")
        # check if there is no project with that name
        if not request.form['project_name'] in u['projects']:
            return jsonify(FAIL="There is no project with that name.")
        # get the user's client ID
        c_id = u['client']
        # remove the project from MongoDB
        p_list, p_n = u['projects'], request.form['project_name']
        p_list.remove(p_n)
        usersDB.update({'email': userEmail}, {'$set': {'projects': p_list}})
        # remove the project from the server
        p_path = '{}/clients/{}/{}/{}/'.format(DIR, c_id, userEmail, p_n)
        try:
            shutil.rmtree(p_path)
        except:
            pass
        # log it
        p_l = generate_timestamp()
        with codecs.open('{}/clients/{}/{}/log.txt'.format(DIR, c_id, userEmail), 'a', 'utf-8') as f:
            f.write('{} D\n'.format(p_l))
        return jsonify(SUCCESS="Project was removed.")
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/renameproject", methods=['POST'])
def rename_project():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a project name
        if 'old_name' not in request.form or 'new_name' not in request.form:
            return jsonify(ERROR="Please enter the old and new name of the project.")
        # check if there is no project with that name
        if not request.form['old_name'] in u['projects']:
            return jsonify(FAIL="There is no project with that name.")
        # check if a project with that name already exists
        if request.form['new_name'] in u['projects']:
            return jsonify(EXISTS="A project with that name already exists.")
        # get the user's client ID
        c_id = u['client']
        # rename the project in MongoDB
        p_list = u['projects']
        p_list_updated = [request.form['new_name'] if x==request.form['old_name'] else x for x in p_list]
        usersDB.update({'email': userEmail}, {'$set': {'projects': p_list_updated}})
        # rename the project folder on the server
        p_old_path = '{}/clients/{}/{}/{}/'.format(DIR, c_id, userEmail, request.form['old_name'])
        p_new_path = '{}/clients/{}/{}/{}/'.format(DIR, c_id, userEmail, request.form['new_name'])
        shutil.move(p_old_path, p_new_path)
        # last step - generate a timestamp & update the current project's timestamp
        p_l = generate_timestamp()
        with codecs.open('{}/clients/{}/{}/{}/last_edited.txt'.format(DIR, c_id, userEmail, request.form['new_name']), 'w', 'utf-8') as f:
            f.write(p_l)
        # log it
        with codecs.open('{}/clients/{}/{}/log.txt'.format(DIR, c_id, userEmail), 'a', 'utf-8') as f:
            f.write('{} R\n'.format(p_l))
        return jsonify(SUCCESS="Project was renamed.")
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/setcurrentproject", methods=['POST'])
def set_current_project():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a project name
        if 'project_name' not in request.form:
            return jsonify(ERROR="Please enter the project name.")
        # check if there is no project with that name
        if not request.form['project_name'] in u['projects']:
            return jsonify(FAIL="There is no project with that name.")
        # check if this project is already the current project
        if request.form['project_name'] == u['projects'][0]:
            return jsonify(DENIED="This project is already the current project.")
        # get the user's client ID
        c_id = u['client']
        # generate a timestamp
        p_l = generate_timestamp()
        # record the name of the current project & edit its timestamp
        p_n = u['projects'][0]
        with codecs.open('{}/clients/{}/{}/{}/last_edited.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f:
            f.write(p_l)
        # set the new project as current in MongoDB
        p_list, p_n = u['projects'], request.form['project_name']
        p_list.remove(p_n)
        p_list_updated = [p_n] + p_list
        usersDB.update({'email': userEmail}, {'$set': {'projects': p_list_updated}})
        # update the new current project's timestamp
        with codecs.open('{}/clients/{}/{}/{}/last_edited.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f:
            f.write(p_l)
        return jsonify(SUCCESS="Project was set as current.")
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/setprojectsecurity", methods=['POST'])
def set_project_security():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a project name and security level
        if 'project_name' not in request.form or 'security' not in request.form:
            return jsonify(ERROR="Please enter the project name and desired security level.")
        # check if there is no project with that name
        if not request.form['project_name'] in u['projects']:
            return jsonify(FAIL="There is no project with that name.")
        # get the user's client ID
        c_id = u['client']
        # check if this project already has this security level
        with codecs.open('{}/clients/{}/{}/{}/secure.txt'.format(DIR, c_id, userEmail, request.form['project_name']), 'r', 'utf-8') as f:
            temp = f.read()
        p_s = int(temp.strip())
        if p_s == int(request.form['security'].strip()):
            return jsonify(DENIED="The project already has this level of security.")
        # update the project's security level
        with codecs.open('{}/clients/{}/{}/{}/secure.txt'.format(DIR, c_id, userEmail, request.form['project_name']), 'w', 'utf-8') as f:
            f.write(request.form['security'].strip())
        # last step - generate a timestamp & update the current project's timestamp
        p_l = generate_timestamp()
        with codecs.open('{}/clients/{}/{}/{}/last_edited.txt'.format(DIR, c_id, userEmail, request.form['project_name']), 'w', 'utf-8') as f:
            f.write(p_l)
        # log it
        l_s = 'S' if int(request.form['security'].strip()) == 1 else 'N'
        with codecs.open('{}/clients/{}/{}/log.txt'.format(DIR, c_id, userEmail), 'a', 'utf-8') as f:
            f.write('{} {}\n'.format(p_l, l_s))
        return jsonify(SUCCESS="Project's security level was changed.")
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/submitstep1data", methods=['POST'])
def submit_step1_data():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a current project
        if u['projects'] == []:
            return jsonify(FAIL="There is no current project.")
        # get the user's client ID
        c_id = u['client']
        # if the user is on a subscription, make sure this search won't exceed their usage cap
        if c_id in CLIENTS_SUBSCRIPTION:
            if get_client_searches(c_id, usersDB) >= CLIENTS_SUBSCRIPTION[c_id][1]:
                return jsonify(CAP_REACHED="You have reached the usage cap for your subscription. Please contact an administrator at your organization to purchase additional searches.")
            if plan_expired(c_id):
                return jsonify(CAP_REACHED="Your subscription has expired. Please contact an administrator at your organization to extend your subscription.")
        # get the current project's name
        p_n = u['projects'][0]
        # convert the input section int to String
        s = chr(ord(request.form['cpc_section'])+16) # e.g. '1' --> 'A'
        # check if there is a priority date
        # first, try to remove any previously stored priority dates
        safe_remove('{}/clients/{}/{}/{}/priority_date.txt'.format(DIR, c_id, userEmail, p_n))
        if 'priority_date' in request.form:
            with codecs.open('{}/clients/{}/{}/{}/priority_date.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f_out:
                f_out.write(request.form['priority_date'].strip())
        # try to get the term frequencies from the input text
        tf, num_words = run.get_term_frequencies(request.form['description'])
        if not tf: # if there's a problem with the description
            return jsonify(FIELDLEVEL_ERROR={'description': 'Please describe your invention with more specificity.'})
        # generate the input vector and classify it
        run.step_1_submit(tf, num_words, s, c_id, userEmail, p_n)
        # record the input in a text file
        with codecs.open('{}/clients/{}/{}/{}/input_text.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f_out:
            f_out.write(request.form['description'])
        # remove data from later steps
        safe_remove_all('{}/clients/{}/{}/{}'.format(DIR, c_id, userEmail, p_n), list(REMOVE_FILENAMES_1))
        # remove any old summaries (.docx files in the project folder)
        curr_dir = '{}/clients/{}/{}/{}/'.format(DIR, c_id, userEmail, p_n)
        old_docx = os.listdir(curr_dir)
        for doc in old_docx:
            if doc.endswith(".docx"):
                os.remove(os.path.join(curr_dir, doc))
        # last step - generate a timestamp & update the current project's timestamp
        p_l = generate_timestamp()
        with codecs.open('{}/clients/{}/{}/{}/last_edited.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f:
            f.write(p_l)
        # log it
        with codecs.open('{}/clients/{}/{}/log.txt'.format(DIR, c_id, userEmail), 'a', 'utf-8') as f:
            if 'priority_date' in request.form:
                f.write('{} 1 {} {} {} {}\n'.format(p_l, len(request.form['description']), len(request.form['description'].split()), s, request.form['priority_date'].strip()))
            else:
                f.write('{} 1 {} {} {}\n'.format(p_l, len(request.form['description']), len(request.form['description'].split()), s))
        return jsonify(SUCCESS="Step 1 completed.")
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/submitstep1dataX", methods=['POST'])
def submit_step1_dataX():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a current project
        if u['projects'] == []:
            return jsonify(FAIL="There is no current project.")
        # get the user's client ID
        c_id = u['client']
        # check if it's a trial user and they exceeded their monthly cap
        if c_id == 'trial' and u['num_searches'] >= MAX_TRIAL_SEARCHES:
            return jsonify(CAP_REACHED="You have reached the maximum number of free searches for your trial account. Please contact the Legalicity team to request more searches.")
        # if the user is on a subscription, make sure this search won't exceed their usage cap
        if c_id in CLIENTS_SUBSCRIPTION:
            if get_client_searches(c_id, usersDB) >= CLIENTS_SUBSCRIPTION[c_id][1]:
                return jsonify(CAP_REACHED="You have reached the usage cap for your subscription. Please contact an administrator at your organization to purchase additional searches.")
            if plan_expired(c_id):
                return jsonify(CAP_REACHED="Your subscription has expired. Please contact an administrator at your organization to extend your subscription.")
        # try to get the term frequencies from the input text
        tf, num_words = run.get_term_frequencies(request.form['description'])
        if not tf: # if there's a problem with the description
            return jsonify(FIELDLEVEL_ERROR={'description': 'Please describe your invention with more specificity.'})
        # get the current project's name
        p_n = u['projects'][0]
        # try to remove any previously stored priority dates
        safe_remove('{}/clients/{}/{}/{}/priority_date.txt'.format(DIR, c_id, userEmail, p_n))
        # check if there is a priority date and save it
        if 'priority_date' in request.form:
            with codecs.open('{}/clients/{}/{}/{}/priority_date.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f_out:
                f_out.write(request.form['priority_date'].strip())
        # check for any known prior art
        known_prior_art = []
        for i in range(1, MAX_KNOWN_PRIOR_ART+1):
            if 'patent_'+str(i) in request.form:
                known_prior_art.append(request.form['patent_'+str(i)])
        # if there's at least one known prior art entered
        if known_prior_art:
            # check for any errors (duplicates or PA not in our database)
            known_prior_art = run.check_known_prior_art(known_prior_art)
            if type(known_prior_art) is dict: # if there's at least one error
                return jsonify(FIELDLEVEL_ERROR=known_prior_art)
            else: # no error - save the known prior art
                with codecs.open('{}/clients/{}/{}/{}/known_prior_art.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f_out:
                    f_out.write('\n'.join(known_prior_art))
        # generate the input vector and classify it
        run.step_1_submitX(tf, num_words, known_prior_art, c_id, userEmail, p_n)
        # record the input in a text file
        with codecs.open('{}/clients/{}/{}/{}/input_text.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f_out:
            f_out.write(request.form['description'])
        # remove data from later steps
        safe_remove_all('{}/clients/{}/{}/{}'.format(DIR, c_id, userEmail, p_n), list(REMOVE_FILENAMES_1))
        # remove any old summaries (.docx files in the project folder)
        curr_dir = '{}/clients/{}/{}/{}/'.format(DIR, c_id, userEmail, p_n)
        old_docx = os.listdir(curr_dir)
        for doc in old_docx:
            if doc.endswith(".docx"):
                os.remove(os.path.join(curr_dir, doc))
        # increment number of searches user has conducted in MongoDB
        usersDB.update(u, {'$inc': {'num_searches': 1}})
        # increment number of searches user has conducted on the server
        with codecs.open('{}/clients/{}/{}/{}/#_searches.txt'.format(DIR, c_id, userEmail, p_n), 'r+', 'utf-8') as f:
            temp = f.read()
            f.seek(0)
            f.write('{}'.format(int(temp.strip())+1))
            f.truncate()
        # last step - generate a timestamp & update the current project's timestamp
        p_l = generate_timestamp()
        with codecs.open('{}/clients/{}/{}/{}/last_edited.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f:
            f.write(p_l)
        # log it
        with codecs.open('{}/clients/{}/{}/log.txt'.format(DIR, c_id, userEmail), 'a', 'utf-8') as f:
            # base
            to_record = '{} 1 {} {}'.format(p_l, len(request.form['description']), len(request.form['description'].split()))
            # add priority date, if any
            if 'priority_date' in request.form:
                to_record = to_record + ' ' + request.form['priority_date'].strip()
            # add known prior art, if any
            if known_prior_art:
                to_record = to_record + ' ' + str(len(known_prior_art))
            f.write('{}\n'.format(to_record))
        return jsonify(SUCCESS="Step 1 completed.")
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/getstep1data", methods=['GET'])
def get_step1_data():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a current project
        if u['projects'] == []:
            return jsonify(FAIL="There is no current project.")
        # get the user's client ID
        c_id = u['client']
        # get the current project's name
        p_n = u['projects'][0]
        # make sure there is stored data for the current project
        if not os.path.exists('{}/clients/{}/{}/{}/input_text.txt'.format(DIR, c_id, userEmail, p_n)):
            return jsonify(description=None, key_elements=None, cpc_section=None, priority_date=None)
        # retrieve the stored input data
        # (1) description
        with codecs.open('{}/clients/{}/{}/{}/input_text.txt'.format(DIR, c_id, userEmail, p_n), 'r', 'utf-8') as f:
            temp = f.read()
        d = temp.strip()
        # (2) CPC section
        with codecs.open('{}/clients/{}/{}/{}/cpc_section.txt'.format(DIR, c_id, userEmail, p_n), 'r', 'utf-8') as f:
            temp = f.read()
        s = int(chr(ord(temp.strip())-16)) # e.g. 'A' --> '1'
        # (3) priority date, if any
        if os.path.exists('{}/clients/{}/{}/{}/priority_date.txt'.format(DIR, c_id, userEmail, p_n)):
            with codecs.open('{}/clients/{}/{}/{}/priority_date.txt'.format(DIR, c_id, userEmail, p_n), 'r', 'utf-8') as f:
                temp = f.read()
            p = temp.strip()
        else:
            p = None
        return jsonify(description=d, cpc_section=s, priority_date=p)
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/getstep1dataX", methods=['GET'])
def get_step1_dataX():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a current project
        if u['projects'] == []:
            return jsonify(FAIL="There is no current project.")
        # get the user's client ID
        c_id = u['client']
        # get the current project's name
        p_n = u['projects'][0]
        # make sure there is stored data for the current project
        if not os.path.exists('{}/clients/{}/{}/{}/input_text.txt'.format(DIR, c_id, userEmail, p_n)):
            return jsonify(description=None, priority_date=None, known_prior_art=None)
        # retrieve the stored input data
        # (1) description
        with codecs.open('{}/clients/{}/{}/{}/input_text.txt'.format(DIR, c_id, userEmail, p_n), 'r', 'utf-8') as f:
            temp = f.read()
        d = temp.strip()
        # (2) priority date, if any
        if os.path.exists('{}/clients/{}/{}/{}/priority_date.txt'.format(DIR, c_id, userEmail, p_n)):
            with codecs.open('{}/clients/{}/{}/{}/priority_date.txt'.format(DIR, c_id, userEmail, p_n), 'r', 'utf-8') as f:
                temp = f.read()
            p = temp.strip()
        else:
            p = None
        # (3) known prior art, if any
        if os.path.exists('{}/clients/{}/{}/{}/known_prior_art.txt'.format(DIR, c_id, userEmail, p_n)):
            with codecs.open('{}/clients/{}/{}/{}/known_prior_art.txt'.format(DIR, c_id, userEmail, p_n), 'r', 'utf-8') as f:
                k = ['US'+line.strip() if line.strip()[0].isdigit() else line.strip() for line in f]
        else:
            k = None
        return jsonify(description=d, priority_date=p, known_prior_art=k)
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/getstep2classes", methods=['GET'])
def get_step2_classes():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a current project
        if u['projects'] == []:
            return jsonify(FAIL="There is no current project.")
        # get the user's client ID
        c_id = u['client']
        # get the current project's name
        p_n = u['projects'][0]
        # make sure there is stored data for the current project
        if not os.path.exists('{}/clients/{}/{}/{}/input_subclasses.txt'.format(DIR, c_id, userEmail, p_n)):
            return jsonify(description=None, key_elements=None, cpc_section=None)
        # get the CPC section
        with codecs.open('{}/clients/{}/{}/{}/cpc_section.txt'.format(DIR, c_id, userEmail, p_n), 'r', 'utf-8') as f:
            temp = f.read()
        s = int(chr(ord(temp.strip())-16)) # e.g. 'A' --> '1'
        return jsonify(cpc_classes=run.get_CPC_classes(c_id, userEmail, p_n), cpc_section=s)
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/getstep2classesX", methods=['POST'])
def get_step2_classesX():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a current project
        if u['projects'] == []:
            return jsonify(FAIL="There is no current project.")
        # get the user's client ID
        c_id = u['client']
        # get the current project's name
        p_n = u['projects'][0]
        # make sure there is stored data for the current project
        if not os.path.exists('{}/clients/{}/{}/{}/input_subclasses.txt'.format(DIR, c_id, userEmail, p_n)):
            return jsonify(cpc_classes=None)
        # make sure the user selected a CPC section
        if 'cpc_section' not in request.form:
            return jsonify(cpc_classes=None)
        # save the CPC section
        with codecs.open('{}/clients/{}/{}/{}/cpc_section.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f_out:
            f_out.write(request.form['cpc_section'])
        # convert the CPC section
        s = int(chr(ord(request.form['cpc_section'])-16)) # e.g. 'A' --> '1'
        return jsonify(cpc_classes=run.get_CPC_classesX(request.form['cpc_section'], c_id, userEmail, p_n), cpc_section=s)
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/getstep2subclasses", methods=['POST'])
def get_step2_subclasses():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a current project
        if u['projects'] == []:
            return jsonify(FAIL="There is no current project.")
        # get the user's client ID
        c_id = u['client']
        # get the current project's name
        p_n = u['projects'][0]
        # make sure there is stored data for the current project
        if not os.path.exists('{}/clients/{}/{}/{}/input_subclasses.txt'.format(DIR, c_id, userEmail, p_n)):
            return jsonify(description=None, key_elements=None, cpc_section=None)
        # get the possible class options
        cpc_classes = run.get_CPC_classes(c_id, userEmail, p_n)
        # check if user selected ANY of these options
        s_c = request.form['cpc_classes'].split(',') if 'cpc_classes' in request.form else [] # get the submitted classes
        chosen_classes = [c['n'] for c in cpc_classes if c['n'] in s_c]
        # if the user hasn't selected any valid options
        if not chosen_classes:
            return jsonify(DENIED="You have not selected any CPC classes.")
        # get the CPC section
        with codecs.open('{}/clients/{}/{}/{}/cpc_section.txt'.format(DIR, c_id, userEmail, p_n), 'r', 'utf-8') as f:
            temp = f.read()
        s = int(chr(ord(temp.strip())-16)) # e.g. 'A' --> '1'
        # last step - generate a timestamp & update the current project's timestamp
        p_l = generate_timestamp()
        with codecs.open('{}/clients/{}/{}/{}/last_edited.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f:
            f.write(p_l)
        return jsonify(cpc_subclasses=run.get_CPC_subclasses(chosen_classes, c_id, userEmail, p_n), cpc_section=s)
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/submitstep2data", methods=['POST'])
def submit_step2_data():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a current project
        if u['projects'] == []:
            return jsonify(FAIL="There is no current project.")
        # get the user's client ID
        c_id = u['client']
        # get the current project's name
        p_n = u['projects'][0]
        # make sure there is stored data for the current project
        if not os.path.exists('{}/clients/{}/{}/{}/input_subclasses.txt'.format(DIR, c_id, userEmail, p_n)):
            return jsonify(MISSING="There is no stored data.")
        # get the possible subclass options
        cpc_subclasses = [c[0] for c in run.get_all_CPC_subclasses(c_id, userEmail, p_n)]
        # check if user selected ANY of these options
        s_sc = request.form['cpc_subclasses'].split(',') if 'cpc_subclasses' in request.form else [] # get the submitted subclasses
        chosen_subclasses = [c for c in cpc_subclasses if c in s_sc]
        # if the user hasn't selected any valid options
        if not chosen_subclasses:
            return jsonify(DENIED="You have not selected any valid CPC subclasses.")
        # check if the user selected more than 5 subclasses
        if len(chosen_subclasses) > 5:
            return jsonify(DENIED="You can't select more than 5 CPC subclasses! Please try again.")
        # check if it's a trial user and they exceeded their monthly cap
        if c_id == 'trial' and u['num_searches'] >= MAX_TRIAL_SEARCHES:
            return jsonify(CAP_REACHED="You have reached the maximum number of free searches for your trial account. Please contact the Legalicity team to request more searches.")
        # if the user is on a subscription, make sure this search won't exceed their usage cap
        if c_id in CLIENTS_SUBSCRIPTION:
            if get_client_searches(c_id, usersDB) >= CLIENTS_SUBSCRIPTION[c_id][1]:
                return jsonify(CAP_REACHED="You have reached the usage cap for your subscription. Please contact an administrator at your organization to purchase additional searches.")
            if plan_expired(c_id):
                return jsonify(CAP_REACHED="Your subscription has expired. Please contact an administrator at your organization to extend your subscription.")
        # save the chosen subclasses for the future
        run.save_chosen_subclasses(chosen_subclasses, c_id, userEmail, p_n)
        if os.path.exists('{}/clients/{}/{}/{}/priority_date.txt'.format(DIR, c_id, userEmail, p_n)):
            with codecs.open('{}/clients/{}/{}/{}/priority_date.txt'.format(DIR, c_id, userEmail, p_n), 'r', 'utf-8') as f:
                temp = f.read()
            priority_date = int(temp.strip().replace('-', ''))
        else:
            priority_date = -1
        # get the prior art and save it
        pa = run.get_prior_art(chosen_subclasses, c_id, userEmail, p_n, priority_date)
        # get the result elements and save them
        run.get_result_elements(pa[:MAX_PRIOR_ART], c_id, userEmail, p_n)
        #except Exception as e:
            #with codecs.open('{}/clients/{}/{}/errors.txt'.format(DIR, c_id, userEmail), 'w', 'utf-8') as f:
                #f.write(str(e))
            #resp = jsonify(msg=str(e))
            #resp.status_code = 406
            #return resp
        # increment number of searches user has conducted in MongoDB
        usersDB.update(u, {'$inc': {'num_searches': 1}})
        # increment number of searches user has conducted on the server
        with codecs.open('{}/clients/{}/{}/{}/#_searches.txt'.format(DIR, c_id, userEmail, p_n), 'r+', 'utf-8') as f:
            temp = f.read()
            f.seek(0)
            f.write('{}'.format(int(temp.strip())+1))
            f.truncate()
        # remove data from later steps
        safe_remove_all('{}/clients/{}/{}/{}'.format(DIR, c_id, userEmail, p_n), list(REMOVE_FILENAMES_2))
        # last step - generate a timestamp & update the current project's timestamp
        p_l = generate_timestamp()
        with codecs.open('{}/clients/{}/{}/{}/last_edited.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f:
            f.write(p_l)
        # log it
        with codecs.open('{}/clients/{}/{}/log.txt'.format(DIR, c_id, userEmail), 'a', 'utf-8') as f:
            f.write('{} 2 {}\n'.format(p_l, ';'.join(chosen_subclasses)))
        with codecs.open('{}/clients/{}/{}/usage.txt'.format(DIR, c_id, userEmail), 'a', 'utf-8') as f:
            f.write('{} S {}\n'.format(p_l.split()[0], p_n))
        return jsonify(SUCCESS="Step 2 completed.")
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/submitstep2dataX", methods=['POST'])
def submit_step2_dataX():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a current project
        if u['projects'] == []:
            return jsonify(FAIL="There is no current project.")
        # get the user's client ID
        c_id = u['client']
        # get the current project's name
        p_n = u['projects'][0]
        # make sure there is stored data for the current project
        if not os.path.exists('{}/clients/{}/{}/{}/input_subclasses.txt'.format(DIR, c_id, userEmail, p_n)):
            return jsonify(MISSING="There is no stored data.")
        # get the possible subclass options
        cpc_subclasses = [c[0] for c in run.get_all_CPC_subclasses(c_id, userEmail, p_n)]
        # check if user selected ANY of these options
        s_sc = request.form['cpc_subclasses'].split(',') if 'cpc_subclasses' in request.form else [] # get the submitted subclasses
        chosen_subclasses = [c for c in cpc_subclasses if c in s_sc]
        # if the user hasn't selected any valid options
        if not chosen_subclasses:
            return jsonify(DENIED="You have not selected any valid CPC subclasses.")
        # check if the user selected more than 5 subclasses
        if len(chosen_subclasses) > 5:
            return jsonify(DENIED="You can't select more than 5 CPC subclasses! Please try again.")
        # save the chosen subclasses for the future
        run.save_chosen_subclasses(chosen_subclasses, c_id, userEmail, p_n)
        if os.path.exists('{}/clients/{}/{}/{}/priority_date.txt'.format(DIR, c_id, userEmail, p_n)):
            with codecs.open('{}/clients/{}/{}/{}/priority_date.txt'.format(DIR, c_id, userEmail, p_n), 'r', 'utf-8') as f:
                temp = f.read()
            priority_date = int(temp.strip().replace('-', ''))
        else:
            priority_date = -1
        # get the prior art and save it
        pa = run.step_2_get_prior_art(chosen_subclasses, c_id, userEmail, p_n, priority_date)
        # get the top applicants and save them
        run.get_top_applicants(pa, c_id, userEmail, p_n)
        # get the result elements and save them
        run.get_result_elements(pa, c_id, userEmail, p_n)
        # remove data from later steps
        safe_remove_all('{}/clients/{}/{}/{}'.format(DIR, c_id, userEmail, p_n), list(REMOVE_FILENAMES_2))
        # last step - generate a timestamp & update the current project's timestamp
        p_l = generate_timestamp()
        with codecs.open('{}/clients/{}/{}/{}/last_edited.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f:
            f.write(p_l)
        # log it
        with codecs.open('{}/clients/{}/{}/log.txt'.format(DIR, c_id, userEmail), 'a', 'utf-8') as f:
            f.write('{} 2 {}\n'.format(p_l, ';'.join(chosen_subclasses)))
        with codecs.open('{}/clients/{}/{}/usage.txt'.format(DIR, c_id, userEmail), 'a', 'utf-8') as f:
            f.write('{} S {}\n'.format(p_l.split()[0], p_n))
        return jsonify(SUCCESS="Step 2 completed.")
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/getstep3results", methods=['POST'])
def get_step3_results():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a current project
        if u['projects'] == []:
            return jsonify(FAIL="There is no current project.")
        # get the user's client ID
        c_id = u['client']
        # get the current project's name
        p_n = u['projects'][0]
        # make sure there are stored prior art results
        if not os.path.exists('{}/clients/{}/{}/{}/prior_art_results.txt'.format(DIR, c_id, userEmail, p_n)):
            return jsonify(prior_art_results=None, heading='NO RESULTS')
        # get the current prior art results
        if 'filtered' in request.form and int(request.form['filtered'].strip()) == 1 and os.path.exists('{}/clients/{}/{}/{}/filtered_results.txt'.format(DIR, c_id, userEmail, p_n)):
            pa = run.read_prior_art('{}/clients/{}/{}/{}/filtered_results.txt'.format(DIR, c_id, userEmail, p_n))
            h = 'FILTERED RESULTS'
        elif os.path.exists('{}/clients/{}/{}/{}/updated_results_current.txt'.format(DIR, c_id, userEmail, p_n)):
            pa = run.read_prior_art('{}/clients/{}/{}/{}/updated_results_current.txt'.format(DIR, c_id, userEmail, p_n))[:MAX_PRIOR_ART]
            h = 'UPDATED RESULTS'
        else:
            pa = run.read_prior_art('{}/clients/{}/{}/{}/prior_art_results.txt'.format(DIR, c_id, userEmail, p_n))[:MAX_PRIOR_ART]
            h = 'TOP RESULTS'
        # make sure it's not empty
        if not pa:
            return jsonify(prior_art_results=None)
        # omit any prior art on the deleted list
        pa_ok = run.check_deleted_prior_art(pa, c_id, userEmail, p_n)
        # make sure it's not empty
        if not pa_ok:
            return jsonify(prior_art_results=None)
        # get the saved prior art, if any
        pa_saved = run.read_prior_art('{}/clients/{}/{}/{}/prior_art_saved.txt'.format(DIR, c_id, userEmail, p_n))
        # format the saved prior art
        formatted_results = run.format_prior_art(pa_ok, True, pa_saved)
        if h == 'FILTERED RESULTS':
            # get the filtered results
            filtered_results = run.add_filters_to_results(formatted_results, c_id, userEmail, p_n)
            if not filtered_results:
                return jsonify(prior_art_results=None)
            # return filtered results, with no filters
            return jsonify(prior_art_results=filtered_results, heading=h)
        else:
            # return formatted results & get filters
            return jsonify(prior_art_results=formatted_results, filters=run.get_filters(c_id, userEmail, p_n), heading=h)
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/getstep3resultsX", methods=['POST'])
def get_step3_resultsX():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a current project
        if u['projects'] == []:
            return jsonify(FAIL="There is no current project.")
        # get the user's client ID
        c_id = u['client']
        # get the current project's name
        p_n = u['projects'][0]
        # make sure there are stored prior art results
        if not os.path.exists('{}/clients/{}/{}/{}/prior_art_results.txt'.format(DIR, c_id, userEmail, p_n)):
            return jsonify(prior_art_results=None, heading='NO RESULTS')
        # get the current prior art results
        if 'filtered' in request.form and int(request.form['filtered'].strip()) == 1 and os.path.exists('{}/clients/{}/{}/{}/filtered_results.txt'.format(DIR, c_id, userEmail, p_n)):
            pa = run.read_prior_art('{}/clients/{}/{}/{}/filtered_results.txt'.format(DIR, c_id, userEmail, p_n))
            h = 'FILTERED RESULTS'
        elif os.path.exists('{}/clients/{}/{}/{}/updated_results_current.txt'.format(DIR, c_id, userEmail, p_n)):
            pa = run.read_prior_art_updated_minus_deleted('updated_results_current', c_id, userEmail, p_n)
            h = 'REFINED RESULTS'
        else:
            pa = run.read_prior_art_minus_deleted('prior_art_results', c_id, userEmail, p_n)
            h = 'TOP RESULTS'
        # make sure it's not empty
        if not pa:
            return jsonify(prior_art_results=None)
        # get the saved prior art, if any
        pa_saved = run.read_prior_art('{}/clients/{}/{}/{}/prior_art_saved.txt'.format(DIR, c_id, userEmail, p_n))
        if h == 'FILTERED RESULTS':
            # format the results in light of the saved prior art, and get the filtered results
            filtered_results = run.add_filters_to_resultsX(run.format_prior_art(pa, True, pa_saved), c_id, userEmail, p_n)
            if not filtered_results:
                return jsonify(prior_art_results=None, label="")
            # return filtered results, with no filters
            return jsonify(prior_art_results=filtered_results, heading=h, label="1-{0} out of {0} results".format(len(filtered_results)))
        else:
            # get the page number
            pg = int(request.form['page'].strip())
            # extract the right subset of results; format the results in light of the saved prior art
            formatted_results = run.format_prior_art(pa[(pg-1)*MAX_PRIOR_ARTX:pg*MAX_PRIOR_ARTX], True, pa_saved) if h == 'TOP RESULTS' else run.format_prior_art_updated(pa[(pg-1)*MAX_PRIOR_ARTX:pg*MAX_PRIOR_ARTX], pa_saved)
            # return formatted results & get filters
            return jsonify(prior_art_results=formatted_results, filters=run.get_filtersX(c_id, userEmail, p_n), heading=h, label="{}-{} out of {} results".format((pg-1)*MAX_PRIOR_ARTX+1, min(pg*MAX_PRIOR_ARTX, len(pa)), len(pa)), more=len(pa)>pg*MAX_PRIOR_ARTX, page=pg)
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/getstep3saved", methods=['GET'])
def get_step3_saved():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a current project
        if u['projects'] == []:
            return jsonify(FAIL="There is no current project.")
        # get the user's client ID
        c_id = u['client']
        # get the current project's name
        p_n = u['projects'][0]
        # get the saved prior art
        pa = run.read_prior_art('{}/clients/{}/{}/{}/prior_art_saved.txt'.format(DIR, c_id, userEmail, p_n))
        # make sure it's not empty
        if not pa:
            return jsonify(prior_art_saved=None)
        # format the saved prior art first
        return jsonify(prior_art_saved=run.format_prior_art(pa))
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/saveresult", methods=['POST'])
def save_result():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a current project
        if u['projects'] == []:
            return jsonify(FAIL="There is no current project.")
        # make sure there is a result as input
        if 'p' not in request.form or 'c' not in request.form:
            return jsonify(DENIED="You have not specified a result to save.")
        # get the user's client ID
        c_id = u['client']
        # get the current project's name
        p_n = u['projects'][0]
        # try to add this result to the saved list; remove 'US' from the start of p!
        err = run.add_result_to_saved(request.form['p'][2:], request.form['c'], c_id, userEmail, p_n)
        if err:
            return jsonify(FIELDLEVEL_ERROR=err)
        else:
            # last step - generate a timestamp & update the current project's timestamp
            p_l = generate_timestamp()
            with codecs.open('{}/clients/{}/{}/{}/last_edited.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f:
                f.write(p_l)
            # log it
            with codecs.open('{}/clients/{}/{}/log.txt'.format(DIR, c_id, userEmail), 'a', 'utf-8') as f:
                f.write('{} Y\n'.format(p_l))
            return jsonify(SUCCESS="Result was saved.")
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/saveresultmanual", methods=['POST'])
def save_result_manual():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a current project
        if u['projects'] == []:
            return jsonify(FAIL="There is no current project.")
        # make sure there is a result as input
        if 'result' not in request.form:
            return jsonify(DENIED="You have not specified a result to save manually.")
        # make sure the input is non-empty
        if request.form['result'].strip() == '':
            return jsonify(FIELDLEVEL_ERROR={'manual_saved_result': 'You have not entered anything.'})
        # get the user's client ID
        c_id = u['client']
        # get the current project's name
        p_n = u['projects'][0]
        # try to add this result to the saved list
        err = run.add_result_to_saved_manual(request.form['result'], c_id, userEmail, p_n)
        if err:
            return jsonify(FIELDLEVEL_ERROR=err)
        else:
            # last step - generate a timestamp & update the current project's timestamp
            p_l = generate_timestamp()
            with codecs.open('{}/clients/{}/{}/{}/last_edited.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f:
                f.write(p_l)
            # log it
            with codecs.open('{}/clients/{}/{}/log.txt'.format(DIR, c_id, userEmail), 'a', 'utf-8') as f:
                f.write('{} M\n'.format(p_l))
            return jsonify(SUCCESS="Result was saved manually.")
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/removeresult", methods=['POST'])
def remove_result():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a current project
        if u['projects'] == []:
            return jsonify(FAIL="There is no current project.")
        # make sure there is a result as input
        if 'p' not in request.form:
            return jsonify(DENIED="You have not specified a result to remove.")
        # get the user's client ID
        c_id = u['client']
        # get the current project's name
        p_n = u['projects'][0]
        # try to remove this result from the saved list; remove 'US' from the start of p!
        err = run.remove_result_from_saved(request.form['p'][2:], c_id, userEmail, p_n)
        if err:
            return jsonify(MISSING="This result is not on the saved list.")
        else:
            # last step - generate a timestamp & update the current project's timestamp
            p_l = generate_timestamp()
            with codecs.open('{}/clients/{}/{}/{}/last_edited.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f:
                f.write(p_l)
            # log it
            with codecs.open('{}/clients/{}/{}/log.txt'.format(DIR, c_id, userEmail), 'a', 'utf-8') as f:
                f.write('{} Z\n'.format(p_l))
            return jsonify(SUCCESS="Result was removed.")
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/deleteresult", methods=['POST'])
def delete_result():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a current project
        if u['projects'] == []:
            return jsonify(FAIL="There is no current project.")
        # make sure there is a result as input
        if 'p' not in request.form or 'c' not in request.form:
            return jsonify(DENIED="You have not specified a result to delete.")
        # get the user's client ID
        c_id = u['client']
        # get the current project's name
        p_n = u['projects'][0]
        # try to add this result to the deleted list; remove 'US' from the start of p!
        err = run.add_result_to_deleted(request.form['p'][2:], request.form['c'], c_id, userEmail, p_n)
        if err:
            return jsonify(EXISTS="This result has already been deleted.")
        else:
            # last step - generate a timestamp & update the current project's timestamp
            p_l = generate_timestamp()
            with codecs.open('{}/clients/{}/{}/{}/last_edited.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f:
                f.write(p_l)
            # log it
            with codecs.open('{}/clients/{}/{}/log.txt'.format(DIR, c_id, userEmail), 'a', 'utf-8') as f:
                f.write('{} X\n'.format(p_l))
            return jsonify(SUCCESS="Result was deleted.")
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/applyfilters", methods=['POST'])
def apply_filters():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a current project
        if u['projects'] == []:
            return jsonify(FAIL="There is no current project.")
        # get the user's client ID
        c_id = u['client']
        # get the current project's name
        p_n = u['projects'][0]
        # make sure there are stored prior art results
        if not os.path.exists('{}/clients/{}/{}/{}/prior_art_results.txt'.format(DIR, c_id, userEmail, p_n)):
            return jsonify(prior_art_results=None)
        # get the stored prior art
        if os.path.exists('{}/clients/{}/{}/{}/updated_results_current.txt'.format(DIR, c_id, userEmail, p_n)):
            pa = run.read_prior_art('{}/clients/{}/{}/{}/updated_results_current.txt'.format(DIR, c_id, userEmail, p_n))
        else:
            pa = run.read_prior_art('{}/clients/{}/{}/{}/prior_art_results.txt'.format(DIR, c_id, userEmail, p_n))
        # make sure it's not empty
        if not pa:
            return jsonify(prior_art_results=None)
        # try to get the filters the user entered
        filters, w2v = {}, None
        # (1) check for key elements
        key_elements = []
        for i in range(1, MAX_KEY_ELEMENTS+1):
            if 'element_'+str(i) in request.form:
                key_elements.append(request.form['element_'+str(i)])
        # if there's at least one input key element
        if key_elements:
            # get the CPC section
            with codecs.open('{}/clients/{}/{}/{}/cpc_section.txt'.format(DIR, c_id, userEmail, p_n), 'r', 'utf-8') as f:
                s = f.read().strip()
            # check the key elements to make sure they're not invalid
            err, elems, w2v = run.check_and_save_elements(key_elements, s, c_id, userEmail, p_n)
            if err: # check for an error
                return jsonify(FIELDLEVEL_ERROR={'element_{}'.format(elems['ELEMENT_NUMBER']): elems['ELEMENT_ERROR']})
            filters['key_elements'] = elems
        # (2) check for result elements
        if 'result_elements' in request.form and request.form['result_elements'] != '':
            filters['result_elements'] = request.form['result_elements'].strip().split(',')
        # (3) check for chosen CPC subclasses
        if 'cpc_subclasses' in request.form and request.form['cpc_subclasses'] != '':
            filters['cpc_subclasses'] = request.form['cpc_subclasses'].strip().split(',')
        # (4) check for date_from
        if 'date_from' in request.form and request.form['date_from'] != '':
            filters['date_from'] = int(request.form['date_from'].strip().replace('-', ''))
        # (5) check for date_to
        if 'date_to' in request.form and request.form['date_to'] != '':
            filters['date_to'] = int(request.form['date_to'].strip().replace('-', ''))
        # make sure the user specified at least one filter
        if not filters:
            return jsonify(DENIED="You have not specified any filters.")
        # omit any prior art on the deleted list
        pa_ok = run.check_deleted_prior_art(pa, c_id, userEmail, p_n)
        # make sure it's not empty
        if not pa_ok:
            return jsonify(prior_art_results=None)
        # get the saved prior art, if any
        pa_saved = run.read_prior_art('{}/clients/{}/{}/{}/prior_art_saved.txt'.format(DIR, c_id, userEmail, p_n))
        # format the saved prior art
        formatted_results = run.format_prior_art(pa_ok, True, pa_saved)
        # filter the formatted prior art
        filtered_results = run.filter_results(formatted_results, filters, c_id, userEmail, p_n, w2v)
        # save the filtered results
        run.save_filtered_results(filtered_results, c_id, userEmail, p_n)
        # log it
        p_l = generate_timestamp()
        with codecs.open('{}/clients/{}/{}/log.txt'.format(DIR, c_id, userEmail), 'a', 'utf-8') as f:
            f.write('{} F {}\n'.format(p_l, ';'.join(filters.keys())))
        return jsonify(prior_art_results=filtered_results)
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/applyfiltersX", methods=['POST'])
def apply_filtersX():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a current project
        if u['projects'] == []:
            return jsonify(FAIL="There is no current project.")
        # get the user's client ID
        c_id = u['client']
        # get the current project's name
        p_n = u['projects'][0]
        # make sure there are stored prior art results
        if not os.path.exists('{}/clients/{}/{}/{}/prior_art_results.txt'.format(DIR, c_id, userEmail, p_n)):
            return jsonify(prior_art_results=None)
        # get the stored prior art
        if os.path.exists('{}/clients/{}/{}/{}/updated_results_current.txt'.format(DIR, c_id, userEmail, p_n)):
            pa = run.read_prior_art_updated_minus_deleted('updated_results_current', c_id, userEmail, p_n)
            is_updated = True
        else:
            pa = run.read_prior_art_minus_deleted('prior_art_results', c_id, userEmail, p_n)
            is_updated = False
        # make sure it's not empty
        if not pa:
            return jsonify(prior_art_results=None)
        # try to get the filters the user entered
        filters = {}
        # (1) check for key elements
        key_elements = []
        for i in range(1, MAX_KEY_ELEMENTS+1):
            if 'element_'+str(i) in request.form:
                key_elements.append(request.form['element_'+str(i)])
        # if there's at least one input key element
        if key_elements:
            # check the key elements to make sure they're not invalid
            err, elems = run.check_key_elements(key_elements)
            if err: # check for an error
                return jsonify(FIELDLEVEL_ERROR={'element_{}'.format(elems['ELEMENT_NUMBER']): elems['ELEMENT_ERROR']})
            filters['key_elements'] = elems # list
        # (2) check for result elements
        if 'result_elements' in request.form and request.form['result_elements'] != '':
            filters['result_elements'] = request.form['result_elements'].strip().split(',')
        # (3) check for chosen CPC subclasses
        if 'cpc_subclasses' in request.form and request.form['cpc_subclasses'] != '':
            filters['cpc_subclasses'] = request.form['cpc_subclasses'].strip().split(',')
        # (4) check for applicants
        if 'applicants' in request.form and request.form['applicants'] != '':
            filters['applicants'] = request.form['applicants'].strip().split(',')
        # (5) check for date_from
        if 'date_from' in request.form and request.form['date_from'] != '':
            filters['date_from'] = int(request.form['date_from'].strip().replace('-', ''))
        # (6) check for date_to
        if 'date_to' in request.form and request.form['date_to'] != '':
            filters['date_to'] = int(request.form['date_to'].strip().replace('-', ''))
        # make sure the user specified at least one filter
        if not filters:
            return jsonify(DENIED="You have not specified any filters.")
        # get the saved prior art, if any
        pa_saved = run.read_prior_art('{}/clients/{}/{}/{}/prior_art_saved.txt'.format(DIR, c_id, userEmail, p_n))
        # format the saved prior art
        formatted_results = run.format_prior_art_updated(pa, pa_saved) if is_updated else run.format_prior_art(pa, True, pa_saved)
        # filter the formatted prior art
        filtered_results = run.filter_resultsX(formatted_results, filters, c_id, userEmail, p_n, updated=is_updated)
        # save the filtered results
        run.save_filtered_resultsX(filtered_results, c_id, userEmail, p_n)
        # log it
        p_l = generate_timestamp()
        with codecs.open('{}/clients/{}/{}/log.txt'.format(DIR, c_id, userEmail), 'a', 'utf-8') as f:
            f.write('{} F {}\n'.format(p_l, ';'.join(filters.keys())))
        return jsonify(prior_art_results=filtered_results, label="1-{0} out of {0} results".format(len(filtered_results)) if len(filtered_results) > 0 else "")
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/updateresults", methods=['POST'])
def update_results():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a current project
        if u['projects'] == []:
            return jsonify(FAIL="There is no current project.")
        # get the user's client ID
        c_id = u['client']
        # get the current project's name
        p_n = u['projects'][0]
        # check if the user specified any saved results
        if 'saved_results' not in request.form:
            return jsonify(DENIED="You have not specified any saved prior art.")
        # get the input saved prior art
        try:
            input_saved_pa = [(x.split(':')[0][2:], x.split(':')[1]) for x in request.form['saved_results'].split(',')]
        except:
            return jsonify(FIELDLEVEL_ERROR={"updated_results": "Save at least one new prior art result to update the results."})
        # check if this is not the first iteration
        if os.path.exists('{}/clients/{}/{}/{}/updated_results_input.txt'.format(DIR, c_id, userEmail, p_n)):
            input_saved_pa = run.check_input_for_update_results(input_saved_pa, c_id, userEmail, p_n)
        # make sure user added new saved prior art
        if not input_saved_pa:
            return jsonify(FIELDLEVEL_ERROR={"updated_results": "Save at least one new prior art result to update the results."})
        # save the latest input
        with codecs.open('{}/clients/{}/{}/{}/updated_results_input.txt'.format(DIR, c_id, userEmail, p_n), 'a', 'utf-8') as f:
            f.write('\n'.join(['{}:{}'.format(x, y) for x, y in input_saved_pa])+'\n')
        # get the updated results
        vectors_exist = os.path.exists('{}/clients/{}/{}/{}/updated_results_vectors.txt'.format(DIR, c_id, userEmail, p_n))
        results_exist = os.path.exists('{}/clients/{}/{}/{}/updated_results_previous.txt'.format(DIR, c_id, userEmail, p_n))
        cpc_subclasses = get_list('{}/clients/{}/{}/{}/chosen_subclasses.txt'.format(DIR, c_id, userEmail, p_n))
        if os.path.exists('{}/clients/{}/{}/{}/priority_date.txt'.format(DIR, c_id, userEmail, p_n)):
            with codecs.open('{}/clients/{}/{}/{}/priority_date.txt'.format(DIR, c_id, userEmail, p_n), 'r', 'utf-8') as f:
                temp = f.read()
            priority_date = int(temp.strip().replace('-', ''))
        else:
            priority_date = -1
        pa = run.get_updated_results(input_saved_pa, cpc_subclasses, vectors_exist, results_exist, c_id, userEmail, p_n, priority_date)
        # save the latest data from this iteration
        with codecs.open('{}/clients/{}/{}/{}/updated_results_previous.txt'.format(DIR, c_id, userEmail, p_n), 'a', 'utf-8') as f:
            f.write('\n'.join(['{}:{}'.format(x, y) for x, y in pa[:MAX_PRIOR_ART]])+'\n')
        with codecs.open('{}/clients/{}/{}/{}/updated_results_current.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f:
            f.write('\n'.join(['{}:{}'.format(x, y) for x, y in pa])+'\n')
        # check if there are no results
        if not pa:
            return jsonify(updated_results=None)
        # omit any prior art on the deleted list
        pa_ok = run.check_deleted_prior_art(pa[:MAX_PRIOR_ART], c_id, userEmail, p_n)
        # make sure it's not empty
        if not pa_ok:
            return jsonify(updated_results=None)
        # get the result elements and save them
        run.get_result_elements(pa_ok, c_id, userEmail, p_n, updated=True)
        # get the saved prior art, if any
        pa_saved = run.read_prior_art('{}/clients/{}/{}/{}/prior_art_saved.txt'.format(DIR, c_id, userEmail, p_n))
        # increment number of updates user has conducted in MongoDB
        usersDB.update(u, {'$inc': {'num_updates': 1}})
        # increment number of updates user has conducted on the server
        with codecs.open('{}/clients/{}/{}/{}/#_updates.txt'.format(DIR, c_id, userEmail, p_n), 'r+', 'utf-8') as f:
            temp = f.read()
            f.seek(0)
            f.write('{}'.format(int(temp.strip())+1))
            f.truncate()
        # last step - generate a timestamp & update the current project's timestamp
        p_l = generate_timestamp()
        with codecs.open('{}/clients/{}/{}/{}/last_edited.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f:
            f.write(p_l)
        # log it
        with codecs.open('{}/clients/{}/{}/log.txt'.format(DIR, c_id, userEmail), 'a', 'utf-8') as f:
            f.write('{} U {}\n'.format(p_l, len(input_saved_pa)))
        with codecs.open('{}/clients/{}/{}/usage.txt'.format(DIR, c_id, userEmail), 'a', 'utf-8') as f:
            f.write('{} U {}\n'.format(p_l.split()[0], p_n))
        # format the saved prior art first & get filters
        return jsonify(prior_art_results=run.format_prior_art(pa_ok, True, pa_saved), filters=run.get_filters(c_id, userEmail, p_n))
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/updateresultsX", methods=['POST'])
def update_resultsX():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a current project
        if u['projects'] == []:
            return jsonify(FAIL="There is no current project.")
        # get the user's client ID
        c_id = u['client']
        # get the current project's name
        p_n = u['projects'][0]
        # check if the user specified any saved results
        if 'saved_results' not in request.form:
            return jsonify(DENIED="You have not specified any saved prior art.")
        # get the input saved prior art
        try:
            input_saved_pa = [(x.split(':')[0][2:], x.split(':')[1]) for x in request.form['saved_results'].split(',')]
        except:
            return jsonify(FIELDLEVEL_ERROR={"updated_results": "Save at least one new prior art result to refine the results."})
        # check if this is not the first iteration
        if os.path.exists('{}/clients/{}/{}/{}/updated_results_input.txt'.format(DIR, c_id, userEmail, p_n)):
            input_saved_pa = run.check_input_for_update_results(input_saved_pa, c_id, userEmail, p_n)
        # make sure user added new saved prior art
        if not input_saved_pa:
            return jsonify(FIELDLEVEL_ERROR={"updated_results": "Save at least one new prior art result to refine the results."})
        # get the CPC subclasses
        cpc_subclasses=get_list('{}/clients/{}/{}/{}/chosen_subclasses.txt'.format(DIR, c_id, userEmail, p_n))
        # get the current CPC section & filter out any new saved prior art that's from a different CPC section
        input_saved_pa = [(x, y) for x, y in input_saved_pa if y[0] == cpc_subclasses[0][0]]
        if not input_saved_pa:
            return jsonify(FIELDLEVEL_ERROR={"updated_results": "Save new prior art from the current CPC section."})
        # save the latest input
        with codecs.open('{}/clients/{}/{}/{}/updated_results_input.txt'.format(DIR, c_id, userEmail, p_n), 'a', 'utf-8') as f:
            f.write('\n'.join(['{}:{}'.format(x, y) for x, y in input_saved_pa])+'\n')
        # get the updated results
        pa = run.step_3_get_updated_results(input_saved_pa, cpc_subclasses, c_id, userEmail, p_n)
        # check if there are no results
        if not pa:
            return jsonify(prior_art_results=None)
        # omit any prior art on the deleted list
        #pa_ok = run.check_deleted_prior_art(pa, c_id, userEmail, p_n)
        # make sure it's not empty
        #if not pa_ok:
        #    return jsonify(prior_art_results=None)
        # get the saved prior art, if any
        #pa_saved = run.read_prior_art('{}/clients/{}/{}/{}/prior_art_saved.txt'.format(DIR, c_id, userEmail, p_n))
        # increment number of updates user has conducted in MongoDB
        usersDB.update(u, {'$inc': {'num_updates': 1}})
        # increment number of updates user has conducted on the server
        with codecs.open('{}/clients/{}/{}/{}/#_updates.txt'.format(DIR, c_id, userEmail, p_n), 'r+', 'utf-8') as f:
            temp = f.read()
            f.seek(0)
            f.write('{}'.format(int(temp.strip())+1))
            f.truncate()
        # last step - generate a timestamp & update the current project's timestamp
        p_l = generate_timestamp()
        with codecs.open('{}/clients/{}/{}/{}/last_edited.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f:
            f.write(p_l)
        # log it
        with codecs.open('{}/clients/{}/{}/log.txt'.format(DIR, c_id, userEmail), 'a', 'utf-8') as f:
            f.write('{} U {}\n'.format(p_l, len(input_saved_pa)))
        with codecs.open('{}/clients/{}/{}/usage.txt'.format(DIR, c_id, userEmail), 'a', 'utf-8') as f:
            f.write('{} U {}\n'.format(p_l.split()[0], p_n))
        # extract the right subset of results; format the results in light of the saved prior art
        #formatted_results = run.format_prior_art_updated(pa_ok[:MAX_PRIOR_ARTX], pa_saved)
        # return formatted results & get filters
        #return jsonify(prior_art_results=formatted_results, filters=run.get_filtersX(c_id, userEmail, p_n), label="1-{} out of {} results".format(min(MAX_PRIOR_ARTX, len(pa_ok)), len(pa_ok)), more=len(pa_ok)>MAX_PRIOR_ARTX, page=1)
        return jsonify(SUCCESS="Results were updated.")
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/clearupdated", methods=['POST'])
def clear_updated():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a current project
        if u['projects'] == []:
            return jsonify(FAIL="There is no current project.")
        # get the user's client ID
        c_id = u['client']
        # get the current project's name
        p_n = u['projects'][0]
        # try to remove any data from updating results
        try:
            os.remove('{}/clients/{}/{}/{}/updated_result_elements.txt'.format(DIR, c_id, userEmail, p_n))
            os.remove('{}/clients/{}/{}/{}/updated_results_input.txt'.format(DIR, c_id, userEmail, p_n))
            os.remove('{}/clients/{}/{}/{}/updated_results_vectors.txt'.format(DIR, c_id, userEmail, p_n))
            os.remove('{}/clients/{}/{}/{}/updated_results_previous.txt'.format(DIR, c_id, userEmail, p_n))
            os.remove('{}/clients/{}/{}/{}/updated_results_current.txt'.format(DIR, c_id, userEmail, p_n))
            # last step - generate a timestamp & update the current project's timestamp
            p_l = generate_timestamp()
            with codecs.open('{}/clients/{}/{}/{}/last_edited.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f:
                f.write(p_l)
            # log it
            with codecs.open('{}/clients/{}/{}/log.txt'.format(DIR, c_id, userEmail), 'a', 'utf-8') as f:
                f.write('{} O\n'.format(p_l))
            return jsonify(SUCCESS="Reverted back to original results.")
        except:
            return jsonify(FIELDLEVEL_ERROR={"original_results": "These are the original results."})
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/clearupdatedX", methods=['POST'])
def clear_updatedX():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a current project
        if u['projects'] == []:
            return jsonify(FAIL="There is no current project.")
        # get the user's client ID
        c_id = u['client']
        # get the current project's name
        p_n = u['projects'][0]
        # try to remove any data from updating results
        safe_remove_all('{}/clients/{}/{}/{}'.format(DIR, c_id, userEmail, p_n), ['updated_results_input', 'updated_results_vectors', 'updated_results_current'])
        # last step - generate a timestamp & update the current project's timestamp
        p_l = generate_timestamp()
        with codecs.open('{}/clients/{}/{}/{}/last_edited.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f:
            f.write(p_l)
        # log it
        with codecs.open('{}/clients/{}/{}/log.txt'.format(DIR, c_id, userEmail), 'a', 'utf-8') as f:
            f.write('{} O\n'.format(p_l))
        return jsonify(page=1)
    
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/getresultdetails", methods=['POST'])
def get_result_details():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        if 'result' not in request.form:
            return jsonify(DENIED="You have not specified a result to get the details for.")
        return jsonify(abstract=run.get_abstract(request.form['result'].strip().split(':')[0][2:], request.form['result'].strip().split(':')[1]))
    
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/changepassword", methods=['POST'])
def change_password():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # make sure the user entered all the required information
        if 'current_password' not in request.form or 'new_password' not in request.form or 'confirm_password' not in request.form:
            return jsonify(DENIED="You have not specified all the required information.")
        # make sure the user entered the correct current password
        if u['password'] != request.form['current_password'].strip():
            return jsonify(FIELDLEVEL_ERROR={"profile_current_password": "The password you entered is incorrect."})
        # make sure the new password matches the confirmed password
        if request.form['new_password'].strip() != request.form['confirm_password'].strip():
            return jsonify(FIELDLEVEL_ERROR={"profile_confirmnew_password": "The password you entered doesn't match the new password."})
        # change the user's password in our database
        usersDB.update({'email': userEmail}, {'$set': {'password': request.form['new_password'].strip()}})
        return jsonify(SUCCESS="Your password was changed successfully!")
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/updatepersonal", methods=['POST'])
def update_personal():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # keep track of any changes made
        changes_made = False
        # check for first name
        if 'first_name' in request.form and u['first_name'] != request.form['first_name'].strip():
            # update the user's first name in our database
            usersDB.update({'email': userEmail}, {'$set': {'first_name': request.form['first_name'].strip()}})
            changes_made = True
        # check for last name
        if 'last_name' in request.form and u['last_name'] != request.form['last_name'].strip():
            # update the user's last name in our database
            usersDB.update({'email': userEmail}, {'$set': {'last_name': request.form['last_name'].strip()}})
            changes_made = True
        # check for role
        if 'role' in request.form and u['role'] != request.form['role'].strip():
            # update the user's role in our database
            usersDB.update({'email': userEmail}, {'$set': {'role': request.form['role'].strip()}})
            changes_made = True
        # check for country
        if 'country' in request.form and u['country'] != request.form['country'].strip():
            # update the user's country in our database
            usersDB.update({'email': userEmail}, {'$set': {'country': request.form['country'].strip()}})
            changes_made = True
        # check for region
        if 'region' in request.form and u['region'] != request.form['region'].strip():
            # update the user's country in our database
            usersDB.update({'email': userEmail}, {'$set': {'region': request.form['region'].strip()}})
            changes_made = True
        # finally, return either success or fail, depending if any changes were made
        if changes_made:
            return jsonify(SUCCESS="Your profile was updated successfully!")
        else:
            return jsonify(FAIL="You have not made any changes.")
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/getcurrentusage", methods=['GET'])
def get_current_usage():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # get the user's client ID
        c_id = u['client']
        # make sure this user isn't a trial user 
        if c_id == 'trial':
            return jsonify(cap=None, usage=None, expiry=None)
        # if the client is on a subscription
        if c_id in CLIENTS_SUBSCRIPTION:
            return jsonify(cap=CLIENTS_SUBSCRIPTION[c_id][1], usage=get_client_searches(c_id, usersDB), expiry=get_client_expiry(c_id))
        else:
            return jsonify(cap=None, usage=get_client_usage(c_id, usersDB), expiry=None)
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/getuseraccounts", methods=['GET'])
def get_user_accounts():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # get the user's client ID
        c_id = u['client']
        # make sure this user isn't a trial user and has administrator privileges
        if c_id == 'trial' or u['admin'] == False:
            return jsonify(admin=None, regular=None)
        # get the user accounts - email addresses of admins and regular users
        return jsonify(admin=sorted([x['email'] for x in usersDB.find({"client": c_id}) if x['admin']==True]), regular=sorted([x['email'] for x in usersDB.find({"client": c_id}) if x['admin']==False]))
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/changepayment", methods=['POST'])
def change_payment():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # get the user's client ID
        c_id = u['client']
        # make sure this user isn't a trial user and has administrator privileges
        if c_id == 'trial' or u['admin'] == False or 'stripe_id' not in u:
            return jsonify(DENIED="You do not have administrator status to perform this operation.")
        # make sure the email the user entered is the same one as theirs - not really relevant, but whatever
        if userEmail != request.form['stripeEmail'].strip().lower():
            return jsonify(PAYMENT_ERROR="The email address you entered is incorrect.")
        # try to change the client organization's payment method
        try:
            stripe.Customer.modify(u['stripe_id'], source=request.form['stripeToken'])
        except:
            return jsonify(PAYMENT_ERROR="Not able to update your payment method. Please make sure you entered the correct information and try again.")
        return jsonify(SUCCESS="Your payment method was updated successfully!")
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/recoverpassword", methods=['POST'])
def recover_password():
    if 'email' not in request.form:
        return jsonify(ERROR="You have not entered an email address.")
    userEmail = request.form['email'].strip().lower()
    usersDB = get_mongo_db() # get the users database
    # grab the relevant info stored for this user from the database
    u = usersDB.find_one({'email': userEmail})
    if u == None: # if no such user found
        return jsonify(FIELDLEVEL_ERROR={"email": "The email address you entered was not found."})
    # send an email with a reset password link to this user
    # send a confirmation email to the user
    bod = '<p>Dear NLPatent User,</p>'
    bod += '<p>The following is an automatically-generated link to reset your password:</p>'
    bod += '<p><a href="https://www.NLPatent.com/resetpassword/{}">Click here to reset your password</a></p>'.format(jwt.encode({'email': userEmail}, JWT_PASSWORD_RESET_KEY, algorithm='HS256'))
    bod += '<p>Thank you again for using our product, and please let us know if you have any questions!</p>'
    bod += '<br>Best regards,<br>Stephanie<br>COO, Legalicity'
    msg = Message("Password Reset Link | NLPatent", \
    sender=("Legalicity Team", "stephanie@legali.city"), \
    html=bod, \
    recipients=[userEmail])
    mail.send(msg)
    return jsonify(SUCCESS="A password reset link has been sent to your email address! You can now close this window.")

@app.route("/resetpassword/<token>")
def reset_password(token):
    # check for any errors with the token
    try:
        userEmail = jwt.decode(token, JWT_PASSWORD_RESET_KEY)['email']
    except:
        return render_template('resetpassworderror.html')
        #return "No good: {}".format(token)
    usersDB = get_mongo_db() # get the users database
    # check whether the extracted email exists in our database
    if usersDB.find_one({'email': userEmail}) == None:
        return render_template('resetpassworderror.html')
    # if there are no problems, display the reset password page
    return render_template('resetpassword.html', email_token=token)

@app.route("/changepasswordreset", methods=['POST'])
def change_password_reset():
    # make sure the user entered all the required information
    if 'email_token' not in request.form or 'new_password' not in request.form or 'confirm_password' not in request.form:
        return jsonify(DENIED="You have not specified all the required information.")
    # check for any errors with the token
    try:
        userEmail = jwt.decode(request.form['email_token'].strip(), JWT_PASSWORD_RESET_KEY)['email']
    except:
        return jsonify(FIELDLEVEL_ERROR={"confirm_password": "This reset password link is no longer valid."})
    usersDB = get_mongo_db() # get the users database
    # check whether the extracted email exists in our database
    if usersDB.find_one({'email': userEmail}) == None:
        return jsonify(FIELDLEVEL_ERROR={"confirm_password": "This reset password link is no longer valid."})
    # make sure the new password matches the confirmed password
    if request.form['new_password'].strip() != request.form['confirm_password'].strip():
        return jsonify(FIELDLEVEL_ERROR={"confirm_password": "The password you entered doesn't match the new password."})
    # change the user's password in our database
    usersDB.update({'email': userEmail}, {'$set': {'password': request.form['new_password'].strip()}})
    return jsonify(SUCCESS="Password was changed.")

@app.route("/submitstep3data", methods=['POST'])
def submit_step3_data():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a current project
        if u['projects'] == []:
            return jsonify(FAIL="There is no current project.")
        # get the user's client ID
        c_id = u['client']
        # get the current project's name
        p_n = u['projects'][0]
        # make sure there is stored data for the current project
        if not os.path.exists('{}/clients/{}/{}/{}/input_text'.format(DIR, c_id, userEmail, p_n)) and not os.path.exists('{}/clients/{}/{}/{}/cpc_section.txt'.format(DIR, c_id, userEmail, p_n)):
            return jsonify(MISSING="There is no stored data.")
        # retrieve the stored input data
        # (1) description
        with codecs.open('{}/clients/{}/{}/{}/input_text.txt'.format(DIR, c_id, userEmail, p_n), 'r', 'utf-8') as f:
            temp = f.read()
        d = temp.strip()
        # (2) CPC section
        with codecs.open('{}/clients/{}/{}/{}/cpc_section.txt'.format(DIR, c_id, userEmail, p_n), 'r', 'utf-8') as f:
            temp = f.read()
        s = temp.strip()
        # run the s. 101 prediction
        OA_101_classify.run(d, s, c_id, userEmail, p_n)
        #try:
        #    OA_101_classify.run(d, s, c_id, userEmail, p_n)
        #except Exception as e:
        #    with codecs.open('{}/clients/{}/{}/errors.txt'.format(DIR, c_id, userEmail), 'w', 'utf-8') as f:
        #        f.write(u'Error with s. 101 prediction: {}'.format(str(e)))
        #    return jsonify(msg=str(e))
        # last step - generate a timestamp & update the current project's timestamp
        p_l = generate_timestamp()
        with codecs.open('{}/clients/{}/{}/{}/last_edited.txt'.format(DIR, c_id, userEmail, p_n), 'w', 'utf-8') as f:
            f.write(p_l)
        # log it
        with codecs.open('{}/clients/{}/{}/log.txt'.format(DIR, c_id, userEmail), 'a', 'utf-8') as f:
            f.write('{} 3\n'.format(p_l))
        return jsonify(SUCCESS="Step 3 completed.")
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/getstep4results", methods=['GET'])
def get_step4_results():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a current project
        if u['projects'] == []:
            return jsonify(FAIL="There is no current project.")
        # get the user's client ID
        c_id = u['client']
        # get the current project's name
        p_n = u['projects'][0]
        # try to get the high tech prediction
        x, y, m = -1, -1, 10 # m = like a penalty, depending on CPC subclass
        if os.path.exists('{}/clients/{}/{}/{}/chosen_subclasses.txt'.format(DIR, c_id, userEmail, p_n)) and set(get_list('{}/clients/{}/{}/{}/chosen_subclasses.txt'.format(DIR, c_id, userEmail, p_n))).intersection(CPC_SUBCLASSES_101):
            m = 0
        if os.path.exists('{}/clients/{}/{}/{}/101_high_tech.txt'.format(DIR, c_id, userEmail, p_n)):
            with codecs.open('{}/clients/{}/{}/{}/101_high_tech.txt'.format(DIR, c_id, userEmail, p_n), 'r', 'utf-8') as f:
                temp = f.read()
            x = int(temp.strip().split(':')[0])
            if (x-m) < MIN_PERCENT_101:
                h = None
            else:
                h = {'p': x, 'at_risk': temp.strip().split(':')[1].split(';')}
        else:
            h = None
        # try to get the life sciences prediction
        if os.path.exists('{}/clients/{}/{}/{}/101_life_sciences.txt'.format(DIR, c_id, userEmail, p_n)):
            with codecs.open('{}/clients/{}/{}/{}/101_life_sciences.txt'.format(DIR, c_id, userEmail, p_n), 'r', 'utf-8') as f:
                temp = f.read()
            y = int(temp.strip().split(':')[0])
            if (y-m) < MIN_PERCENT_101:
                l = None
            else:
                # don't display both - only display high tech OR life sciences!
                if y > x: # check if life sciences likelihood > high tech likelihood
                    h = None
                    l = {'p': y, 'at_risk': temp.strip().split(':')[1].split(';')}
                else:
                    l = None
        else:
            l = None
        return jsonify(high_tech=h, life_sciences=l)
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/downloadresults", methods=['GET'])
def download_results():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a current project
        if u['projects'] == []:
            return jsonify(FAIL="There is no current project.")
        # get the user's client ID
        c_id = u['client']
        # get the current project's name
        p_n = u['projects'][0]
        # check if there are any saved prior art results
        if not os.path.exists('{}/clients/{}/{}/{}/prior_art_saved.txt'.format(DIR, c_id, userEmail, p_n)):
            return jsonify(DENIED="You have not saved any Prior Art results.")
        # get the saved prior art
        try:
            pa_saved = run.read_prior_art('{}/clients/{}/{}/{}/prior_art_saved.txt'.format(DIR, c_id, userEmail, p_n))
        except Exception as e:
            return jsonify(msg=str(e))
        # if the file is empty, i.e. there are no saved prior art results
        if not pa_saved:
            return jsonify(DENIED="You have not saved any Prior Art results.")
        # generate Word summary
        user_name = ''
        if u['first_name'] != '': user_name += u['first_name']
        if u['last_name'] != '': user_name += ' ' + u['last_name']
        # first, remove any old summaries (.docx files in the project folder)
        curr_dir = '{}/clients/{}/{}/{}/'.format(DIR, c_id, userEmail, p_n)
        old_docx = os.listdir(curr_dir)
        for doc in old_docx:
            if doc.endswith(".docx"):
                os.remove(os.path.join(curr_dir, doc))
        # then, generate a new summary
        f_name = generate_summary.run(pa_saved, user_name, c_id, userEmail, p_n)
        # log it
        p_l = generate_timestamp()
        with codecs.open('{}/clients/{}/{}/log.txt'.format(DIR, c_id, userEmail), 'a', 'utf-8') as f:
            f.write('{} L\n'.format(p_l))
        return send_from_directory(directory='{}/clients/{}/{}/{}/'.format(DIR, c_id, userEmail, p_n), as_attachment=True, filename=f_name, attachment_filename=f_name)
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/emailresults", methods=['GET'])
def email_results():
    if 'LegalicityCookie' in request.cookies and request.cookies.get('LegalicityCookie') != '':
        auth = request.cookies.get('LegalicityCookie')
        # extract the user's email address from the JWT token
        userEmail = jwt.decode(auth, JWT_SECRET_KEY)['email']
        usersDB = get_mongo_db() # get the users database
        # grab the relevant info stored for this user from the database
        u = usersDB.find_one({'email': userEmail})
        if u == None: # if no such user found
            return jsonify(ERROR="Something went wrong. Please try logging in again.")
        # sanity check to make sure there is a current project
        if u['projects'] == []:
            return jsonify(FAIL="There is no current project.")
        # get the user's client ID
        c_id = u['client']
        # get the current project's name
        p_n = u['projects'][0]
        # check if there are any saved prior art results
        if not os.path.exists('{}/clients/{}/{}/{}/prior_art_saved.txt'.format(DIR, c_id, userEmail, p_n)):
            return jsonify(DENIED="You have not saved any Prior Art results.")
        # get the saved prior art
        try:
            pa_saved = run.read_prior_art('{}/clients/{}/{}/{}/prior_art_saved.txt'.format(DIR, c_id, userEmail, p_n))
        except Exception as e:
            return jsonify(msg=str(e))
        # if the file is empty, i.e. there are no saved prior art results
        if not pa_saved:
            return jsonify(DENIED="You have not saved any Prior Art results.")
        # generate Word summary
        user_name = ''
        if u['first_name'] != '': user_name += u['first_name']
        if u['last_name'] != '': user_name += ' ' + u['last_name']
        # first, remove any old summaries (.docx files in the project folder)
        curr_dir = '{}/clients/{}/{}/{}/'.format(DIR, c_id, userEmail, p_n)
        old_docx = os.listdir(curr_dir)
        for doc in old_docx:
            if doc.endswith(".docx"):
                os.remove(os.path.join(curr_dir, doc))
        # then, generate a new summary
        f_name = generate_summary.run(pa_saved, user_name, c_id, userEmail, p_n)
        send_results(c_id, userEmail, p_n, f_name)
        # log it
        p_l = generate_timestamp()
        with codecs.open('{}/clients/{}/{}/log.txt'.format(DIR, c_id, userEmail), 'a', 'utf-8') as f:
            f.write('{} E\n'.format(p_l))
        return jsonify(SUCCESS="Your results have been emailed to you!")
    else:
        return jsonify(TIMEOUT="Your session has timed out. Please log in again.")

@app.route("/order/<token>")
def order(token):
    # no need to check for errors because I'll be checking it manually before sending the link to the client
    c_id = jwt.decode(token, JWT_CLIENT_KEY)['c_id']
    if c_id in CLIENTS_INVOICING:
        # display the order form for invoicing clients
        if c_id in CLIENTS_SUBSCRIPTION:
            return render_template('order2.html', client_token=token, organization=CLIENTS[c_id], currency=CLIENTS_CURRENCY[c_id], num_months=CLIENTS_SUBSCRIPTION[c_id][0], max_searches=CLIENTS_SUBSCRIPTION[c_id][1], amount_dollars='{:.2f}'.format(CLIENTS_SUBSCRIPTION[c_id][1]*CLIENTS_COST_SEARCH[c_id]*CLIENTS_TAX_RATES[c_id]))
        else:
            t_n, f_i, a_n = BANK_ACCOUNT[CLIENTS_CURRENCY[c_id]] # get the CAD or USD bank account info
            return render_template('order2.html', client_token=token, organization=CLIENTS[c_id], currency=CLIENTS_CURRENCY[c_id], per_search=CLIENTS_COST_SEARCH[c_id], per_update=CLIENTS_COST_UPDATE[c_id], transit_number=t_n, fin_inst=f_i, account_number=a_n)
    else:
        # display the order form for credit card clients
        if c_id in CLIENTS_SUBSCRIPTION:
            return render_template('order.html', client_token=token, organization=CLIENTS[c_id], num_months=CLIENTS_SUBSCRIPTION[c_id][0], max_searches=CLIENTS_SUBSCRIPTION[c_id][1], amount_dollars='{:.2f}'.format(CLIENTS_SUBSCRIPTION[c_id][1]*CLIENTS_COST_SEARCH[c_id]*CLIENTS_TAX_RATES[c_id]), amount_cents=CLIENTS_SUBSCRIPTION[c_id][1]*CLIENTS_COST_SEARCH[c_id]*CLIENTS_TAX_RATES[c_id]*100, key=STRIPE_KEYS['publishable_key'], currency=CLIENTS_CURRENCY[c_id])
        else:
            return render_template('order.html', client_token=token, organization=CLIENTS[c_id], amount_cents=COST_ACTIVATION*CLIENTS_TAX_RATES[c_id]*100, key=STRIPE_KEYS['publishable_key'], currency=CLIENTS_CURRENCY[c_id], per_search=CLIENTS_COST_SEARCH[c_id], per_update=CLIENTS_COST_UPDATE[c_id])

@app.route("/charge", methods=['POST'])
def charge():
    # make sure the user entered all the required information
    if 'client_token' not in request.form or 'admins' not in request.form or 'regular' not in request.form:
        return jsonify(DENIED="You have not specified all the required information.")
    # check for any errors with the token
    try:
        c_id = jwt.decode(request.form['client_token'].strip(), JWT_CLIENT_KEY)['c_id']
    except:
        return jsonify(ERROR="Your order form link is no longer valid.")
    usersDB = get_mongo_db() # get the users database
    # make sure this isn't an existing client organization
    if usersDB.find_one({'client': c_id}) != None:
        return jsonify(ERROR="Your NLPatent account is already active.")
    # check the email addresses
    a_u = [z.strip().lower() for z in request.form['admins'].strip().split(',')]
    r_u = [w.strip().lower() for w in request.form['regular'].strip().split(',')] if request.form['regular'].strip() != '' else []
    combined_u = a_u + r_u
    temp = set()
    for i in range(len(combined_u)): # go through admins & regular users (at least 1 admin!)
        # check for invalid email input, e.g. with spaces or bad characters
        if len(combined_u[i].split()) > 1 or combined_u[i].startswith('(') or combined_u[i].startswith('<'):
            if i >= len(a_u):
                return jsonify(FIELDLEVEL_ERROR={'regular_{}'.format(i-len(a_u)+1): "Invalid format. Please enter an email address."})
            else:
                return jsonify(FIELDLEVEL_ERROR={'administrator_{}'.format(i+1): "Invalid format. Please enter an email address."})
        # check for duplicates in the input
        if combined_u[i] in temp:
            if i >= len(a_u):
                return jsonify(FIELDLEVEL_ERROR={'regular_{}'.format(i-len(a_u)+1): "You have entered this email address twice."})
            else:
                return jsonify(FIELDLEVEL_ERROR={'administrator_{}'.format(i+1): "You have entered this email address twice."})
        temp.add(combined_u[i])
        # check whether the email exists in our database
        u = usersDB.find_one({'email': combined_u[i]})
        if u != None and 'client' in u and u['client'] != 'trial':
            if i >= len(a_u):
                return jsonify(FIELDLEVEL_ERROR={'regular_{}'.format(i-len(a_u)+1): "This email address is associated with another NLPatent account."})
            else:
                return jsonify(FIELDLEVEL_ERROR={'administrator_{}'.format(i+1): "This email address is associated with another NLPatent account."})
    # add a new Stripe user (for the client organization) & try to charge them
    try:
        customer = stripe.Customer.create(description=c_id, source=request.form['stripeToken'])
    except:
        return jsonify(PAYMENT_ERROR="Not able to process your order. Please make sure you entered the correct information and try again.")
    try:
        if c_id in CLIENTS_SUBSCRIPTION:
            charge = stripe.Charge.create(customer=customer.id, amount=int(CLIENTS_SUBSCRIPTION[c_id][1]*CLIENTS_COST_SEARCH[c_id]*CLIENTS_TAX_RATES[c_id]*100), currency=CLIENTS_CURRENCY[c_id], description='NLPatent Subscription Fee', receipt_email=request.form['stripeEmail'])
        else:
            charge = stripe.Charge.create(customer=customer.id, amount=int(COST_ACTIVATION*CLIENTS_TAX_RATES[c_id]*100), currency=CLIENTS_CURRENCY[c_id], description='NLPatent Activation Fee', receipt_email=request.form['stripeEmail'])
    except stripe.error.CardError:
        customer.delete()
        return jsonify(PAYMENT_ERROR="Not able to process your order because your card was declined. Please try again.")
    except Exception as e:
        customer.delete()
        return jsonify(PAYMENT_ERROR="Not able to process your order. Please make sure you entered the correct information and try again.")
    # for subscription orders, calculate & record expiry date
    if c_id in CLIENTS_SUBSCRIPTION:
        try:
            with codecs.open('{}/clients/{}/expiry.txt'.format(DIR, c_id), 'w', 'utf-8') as f:
                f.write('{}'.format(get_forward_daystamp(c_id)))
        except:
            pass # do nothing - shouldn't happen!
    # create new user accounts for all the specified email addresses
    for userEmail in combined_u:
        # make sure to remove any 'trial' or 'pub_trial' users from MongoDB
        if usersDB.find_one({'email': userEmail}) != None:
            usersDB.delete_one({'email': userEmail})
        # also make sure to delete the user's trial folder on the server, if there is one
        if os.path.isdir('{}/clients/trial/{}'.format(DIR, userEmail)):
            try:
                shutil.rmtree('{}/clients/trial/{}'.format(DIR, userEmail), ignore_errors=False, onerror=None)
            except:
                pass # shouldn't happen!
        # create a new MongoDB entry for this user
        p = generate_random_password(6)
        add_normal_user(usersDB, userEmail, p, c_id, admin=userEmail in a_u, ci=customer.id)
        # create a new user folder on the server & add a log entry
        try:
            os.mkdir('{}/clients/{}/{}/'.format(DIR, c_id, userEmail))
        except:
            pass # shouldn't actually happen!
        with codecs.open('{}/clients/{}/{}/log.txt'.format(DIR, c_id, userEmail), 'a', 'utf-8') as f:
            f.write('{} C\n'.format(generate_timestamp()))
        # send email with login credentials
        send_new_user_credentials(userEmail, p, CLIENTS[c_id], admin=userEmail in a_u)

    return jsonify(SUCCESS="Your NLPatent account is now active! The users you listed should receive their login credentials by email shortly.")

@app.route("/placeorder", methods=['POST'])
def place_order():
    # make sure the user entered all the required information
    if 'client_token' not in request.form or 'admins' not in request.form or 'regular' not in request.form:
        return jsonify(DENIED="You have not specified all the required information.")
    # check for any errors with the token
    try:
        c_id = jwt.decode(request.form['client_token'].strip(), JWT_CLIENT_KEY)['c_id']
    except:
        return jsonify(ERROR="Your order form link is no longer valid.")
    usersDB = get_mongo_db() # get the users database
    # make sure this isn't an existing client organization
    if usersDB.find_one({'client': c_id}) != None:
        return jsonify(ERROR="Your NLPatent account is already active.")
    # check the email addresses
    a_u = [z.strip().lower() for z in request.form['admins'].strip().split(',')]
    r_u = [w.strip().lower() for w in request.form['regular'].strip().split(',')] if request.form['regular'].strip() != '' else []
    combined_u = a_u + r_u
    temp = set()
    for i in range(len(combined_u)): # go through admins & regular users (at least 1 admin!)
        # check for invalid email input, e.g. with spaces or bad characters
        if len(combined_u[i].split()) > 1 or combined_u[i].startswith('(') or combined_u[i].startswith('<'):
            if i >= len(a_u):
                return jsonify(FIELDLEVEL_ERROR={'regular_{}'.format(i-len(a_u)+1): "Invalid format. Please enter an email address."})
            else:
                return jsonify(FIELDLEVEL_ERROR={'administrator_{}'.format(i+1): "Invalid format. Please enter an email address."})
        # check for duplicates in the input
        if combined_u[i] in temp:
            if i >= len(a_u):
                return jsonify(FIELDLEVEL_ERROR={'regular_{}'.format(i-len(a_u)+1): "You have entered this email address twice."})
            else:
                return jsonify(FIELDLEVEL_ERROR={'administrator_{}'.format(i+1): "You have entered this email address twice."})
        temp.add(combined_u[i])
        # check whether the email exists in our database
        u = usersDB.find_one({'email': combined_u[i]})
        if u != None and 'client' in u and u['client'] != 'trial':
            if i >= len(a_u):
                return jsonify(FIELDLEVEL_ERROR={'regular_{}'.format(i-len(a_u)+1): "This email address is associated with another NLPatent account."})
            else:
                return jsonify(FIELDLEVEL_ERROR={'administrator_{}'.format(i+1): "This email address is associated with another NLPatent account."})
    # for subscription orders, calculate & record expiry date
    if c_id in CLIENTS_SUBSCRIPTION:
        try:
            with codecs.open('{}/clients/{}/expiry.txt'.format(DIR, c_id), 'w', 'utf-8') as f:
                f.write('{}'.format(get_forward_daystamp(c_id)))
        except:
            pass # do nothing - shouldn't happen!
    # create new user accounts for all the specified email addresses
    for userEmail in combined_u:
        # make sure to remove any 'trial' or 'pub_trial' users from MongoDB
        if usersDB.find_one({'email': userEmail}) != None:
            usersDB.delete_one({'email': userEmail})
        # also make sure to delete the user's trial folder on the server, if there is one
        if os.path.isdir('{}/clients/trial/{}'.format(DIR, userEmail)):
            try:
                shutil.rmtree('{}/clients/trial/{}'.format(DIR, userEmail), ignore_errors=False, onerror=None)
            except:
                pass # shouldn't happen!
        # create a new MongoDB entry for this user
        p = generate_random_password(6)
        add_normal_user(usersDB, userEmail, p, c_id, admin=userEmail in a_u, ci=None)
        # create a new user folder on the server & add a log entry
        try:
            os.mkdir('{}/clients/{}/{}/'.format(DIR, c_id, userEmail))
        except:
            pass # shouldn't actually happen!
        with codecs.open('{}/clients/{}/{}/log.txt'.format(DIR, c_id, userEmail), 'a', 'utf-8') as f:
            f.write('{} C\n'.format(generate_timestamp()))
        # send email with login credentials
        send_new_user_credentials(userEmail, p, CLIENTS[c_id], admin=userEmail in a_u)

    return jsonify(SUCCESS="Your NLPatent account is now active! The users you listed should receive their login credentials by email shortly.")

@app.route("/downloadterms", methods=['POST'])
def download_terms():
    # make sure the user entered all the required information
    if 'client_token' not in request.form:
        return jsonify(DENIED="You have not specified all the required information.")
    # check for any errors with the token
    try:
        c_id = jwt.decode(request.form['client_token'].strip(), JWT_CLIENT_KEY)['c_id']
    except:
        return jsonify(FIELDLEVEL_ERROR={"download_terms": "Your order form link is no longer valid."})
    try:
        dir_name = '{}/clients/{}/'.format(DIR, c_id)
        doc_name = 'Legalicity - Terms of Service - {}.docx'.format(CLIENTS[c_id])
        return send_from_directory(directory=dir_name, as_attachment=True, filename=doc_name, attachment_filename=doc_name)
    except:
        return jsonify(FIELDLEVEL_ERROR={"download_terms": "Not able to download the Terms and Conditions. Please contact the Legalicity team."})

@app.route("/downloadprivacy", methods=['POST'])
def download_privacy():
    # make sure the user entered all the required information
    if 'client_token' not in request.form:
        return jsonify(DENIED="You have not specified all the required information.")
    # check for any errors with the token
    try:
        c_id = jwt.decode(request.form['client_token'].strip(), JWT_CLIENT_KEY)['c_id']
    except:
        return jsonify(FIELDLEVEL_ERROR={"download_privacy": "Your order form link is no longer valid."})
    try:
        dir_name = '{}/clients/{}/'.format(DIR, c_id)
        doc_name = 'Legalicity - Privacy Policy - {}.docx'.format(CLIENTS[c_id])
        return send_from_directory(directory=dir_name, as_attachment=True, filename=doc_name, attachment_filename=doc_name)
    except:
        return jsonify(FIELDLEVEL_ERROR={"download_privacy": "Not able to download the Privacy Policy. Please contact the Legalicity team."})

@app.route("/addtrial", methods=['POST'])
def add_trial():
    # check to make sure there's both a name and an email address
    if not ('name' in request.form and 'email' in request.form):
        return jsonify(ERROR="The information provided is invalid.")
    userName, userEmail = request.form['name'], request.form['email']
    # check if there's referral info
    if 'signup_referral' in request.form:
        r = request.form['signup_referral'].strip()
        if 'signup_referral_other' in request.form:
            r = '{}: {}'.format(r, request.form['signup_referral_other'].strip())
    else:
        r = ''
    # generate a timestamp - different from the usual one, no hours & minutes!
    p_l = generate_daystamp()
    # add this user to the list of trial requests
    with codecs.open('{}/clients/trial/requests.txt'.format(DIR), 'a', 'utf-8') as f:
        if r == '':
            f.write(u'{} | {}: {}\n'.format(p_l, userName, userEmail))
        else:
            f.write(u'{} | {}: {} | {}\n'.format(p_l, userName, userEmail, r))
    return jsonify(added=userEmail) # "Your email has been added to the list: userEmail"

##### MAIN #####

if __name__ == "__main__":
    app.run(threaded=True)
