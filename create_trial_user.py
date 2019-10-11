import os, sys, codecs
from gen_const import DIR
from gen_const import generate_timestamp, get_mongo_db, generate_random_password

##### HOW TO USE #####
# create_trial_user.py [email address] [first name] [last name]
## Example: create_trial_user.py y.riabinin@gmail.com Yaroslav Riabinin

##### MAIN #####

def run(email, first_name, last_name):
    # add new trial user to MongoDB
    usersDB = get_mongo_db()
    # check if this user already exists in our database
    u = usersDB.find_one({'email': email})
    if u != None:
        if 'pub_trial' in u:
            usersDB.delete_one({'email': email})
        elif 'client' in u:
            if u['client'] == 'trial':
                print('This trial user already exists in our database!')
            else:
                print('This user already exists in our database under client: {}'.format(u['client']))
            return
    p = generate_random_password(6) # random 6-character password String
    print('Password: ' + p)
    newUser = {'email': email, 'password': p, 'first_name': first_name, 'last_name': last_name, 'num_searches': 0,
               'num_updates': 0, 'projects': [], 'country': '', 'region': '', 'client': 'trial', 'role': '', 'admin': False}
    usersDB.insert_one(newUser)
    # create a new user folder on the server & add a log entry
    try:
        os.mkdir('{}/clients/{}/{}/'.format(DIR, 'trial', email))
    except:
        pass # shouldn't actually happen!
    with codecs.open('{}/clients/{}/{}/log.txt'.format(DIR, 'trial', email), 'a', 'utf-8') as f:
        f.write('{} C\n'.format(generate_timestamp()))

if '__main__' == __name__:
    try:
        run(sys.argv[1].lower(), sys.argv[2], sys.argv[3])
    except:
        print("There is an error! Try again.")


