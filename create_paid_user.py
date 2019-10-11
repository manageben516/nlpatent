import os, sys, codecs, shutil, smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from gen_const import DIR
from gen_const import generate_timestamp, get_mongo_db, generate_random_password

##### HOW TO USE #####
# create_paid_user.py [email address] [first name] [last name] [client ID] [OPTIONAL: "admin"]
## Example: create_paid_user.py yaroslav@legalicity.net Yaroslav Riabinin lgc
## Example: create_paid_user.py yaroslav@legalicity.net Yaroslav Riabinin lgc admin

##### HELPERS #####

def get_stripe_id(c_id, usersDB):
    s = None
    for u in usersDB.find({"client": "lgc"}):
        if u['admin'] == True and 'stripe_id' in u:
            s = u['stripe_id']
            break
    return s

def send_new_user_credentials(email, password, admin):
    # send this list by email
    fromaddr = 'stephanie@legali.city'
    toaddr = email
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = 'New Account Created | NLPatent'
    body = '<p>Hello,</p>'
    body += '<p>A new NLPatent account was created for you.</p>'
    body += '<p><a href="https://www.nlpatent.com">NLPatent</a> is an online patent search & analysis tool powered by the latest AI.</p>'
    body += "<p>Here are your login credentials:</p>"
    body += "<p><u>Username</u>: {}</p>".format(email)
    body += "<p><u>Password</u>: {}</p>".format(password)
    if admin:
        body += "<p>You also have administrator status, which means you can view the payment method, current usage, and a list of all the user accounts for your client organization.</p>"
    body += "<p>If you ever have any questions or comments about the product please let us know!</p>"
    body += '<br>Best regards,<br>Stephanie<br>COO, Legalicity'
    msg.attach(MIMEText(body, 'html'))
    server = smtplib.SMTP('smtp.office365.com', 587)
    server.starttls()
    server.login(fromaddr, os.environ["EMAIL_PASSWORD"])
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

##### MAIN #####

def run(email, first_name, last_name, c_id, admin=False):
    # add new trial user to MongoDB
    usersDB = get_mongo_db()
    # check if this user already exists in our database
    u = usersDB.find_one({'email': email})
    if u != None:
        if 'client' in u:
            if u['client'] != 'trial':
                print('This user already exists in our database under client: {}'.format(u['client']))
                return
            else:
                # delete this trial user first
                usersDB.delete_one({'email': email})
                if os.path.isdir('{}/clients/trial/{}'.format(DIR, email)):
                    try:
                        shutil.rmtree('{}/clients/trial/{}'.format(DIR, email), ignore_errors=False, onerror=None)
                    except:
                        pass # shouldn't happen!
        else:
            print("This user already exists but under no client organization. Check with Yaro!")
            return
    p = generate_random_password(6) # random 6-character password String
    newUser = {'email': email, 'password': p, 'first_name': first_name, 'last_name': last_name, 'num_searches': 0,
               'num_updates': 0, 'projects': [], 'country': '', 'region': '', 'client': c_id, 'role': '', 'admin': admin}
    payment_credit = False
    # check if the user is an admin
    if admin:
        # try to get the Stripe ID from another admin of this client organization
        stripe_id = get_stripe_id(c_id, usersDB)
        if stripe_id:
            # if there is a Stripe ID, then the client organization is paying by credit card
            payment_credit = True
            newUser['stripe_id'] = stripe_id
    usersDB.insert_one(newUser)
    # create a new user folder on the server & add a log entry
    os.mkdir('{}/clients/{}/{}/'.format(DIR, c_id, email))
    with codecs.open('{}/clients/{}/{}/log.txt'.format(DIR, c_id, email), 'a', 'utf-8') as f:
        f.write('{} C\n'.format(generate_timestamp()))
    # send the user's credentials by email
    send_new_user_credentials(email, p, admin)
    print("Successfully added new user and sent login credentials by email.")
    if admin:
        print("New user is an administrator.")
        if payment_credit:
            print("Client organization is confirmed to be paying by CREDIT CARD.")
        else:
            print("Client organization is confirmed to be paying by INVOICE.")

if '__main__' == __name__:
    try:
        # see if new user should be an admin and what payment method
        admin = sys.argv[5].lower() if len(sys.argv) > 5 else None
        # make sure there are no errors
        if admin and admin != 'admin':
            print("Incorrect format! Try again.")
        else:
            run(sys.argv[1].lower(), sys.argv[2], sys.argv[3], sys.argv[4].lower(), admin != None)
    except:
        print("There is an error! Try again.")


