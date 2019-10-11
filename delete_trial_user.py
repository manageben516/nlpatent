import os, sys, codecs, shutil
from gen_const import DIR
from gen_const import get_mongo_db

##### HOW TO USE #####
# delete_trial_user.py [email address]
## Example: delete_trial_user.py y.riabinin@gmail.com
# delete_trial_user.py all [email address extension]
## Example: delete_trial_user.py all blg.com

##### MAIN #####

def run(x, email_ext=None):
    usersDB = get_mongo_db()
    # check if there's an email extension
    if email_ext:
        # make sure the arguments are in the right format
        if x != 'all':
            print("Incorrect input format! Try again.")
            return
        # get a list of all email addresses to delete
        emails = [u['email'] for u in usersDB.find({"client": "trial"}) if u['email'].endswith('@{}'.format(email_ext.lower()))]
        if not emails:
            print("There are no trial users with this email extension. Try again.")
            return
    else:
        emails = [x]

    # go through all the email addresses to delete
    for e in emails:
        # make sure this user exists
        if not os.path.isdir('{}/clients/trial/{}'.format(DIR, e)):
            print("This trial user doesn't exist! Try again.")
            continue
        # try to save this user's log
        if os.path.exists('{}/clients/trial/{}/log.txt'.format(DIR, e)):
            with codecs.open('{}/clients/trial/{}/log.txt'.format(DIR, e), 'r', 'utf-8') as f_in, codecs.open('{}/logs/{}.txt'.format(DIR, e), 'a', 'utf-8') as f_out:
                f_out.write(f_in.read())
            #print("User's log backed up successfully.")
        # try to remove this user from MongoDB
        try:
            usersDB.delete_one({'email': e})
            #print("User '{}' deleted from MongoDB successfully.".format(e))
        except:
            print("User '{}' wasn't found in MongoDB.".format(e))
        # try to remove this user from the server
        try:
            shutil.rmtree('{}/clients/trial/{}'.format(DIR, e), ignore_errors=False, onerror=None)
            #print("User '{}' deleted from the server successfully.".format(e))
        except:
            print("User '{}' wasn't found on the server.".format(e))
        print("User '{}' deleted successfully.".format(e))

if '__main__' == __name__:
    try:
        email_ext = sys.argv[2].lower() if len(sys.argv) > 2 else None
        run(sys.argv[1].lower(), email_ext)
    except:
        print("There is an error! Try again.")

