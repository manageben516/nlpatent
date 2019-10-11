import os, sys, codecs, re
from gen_const import DIR, EMAIL_PATTERN, CODES, CODE_NAMES, CLIENTS
from datetime import datetime

##### HOW TO USE #####
# get_usage.py ['u'|'a'] ['all'(if 'u')|'trial'|c_id] [o: email(if c_id)|@xyz.com(if 'trial')] [o: month(YYYY-MM)] 

# Examples for Usage:
# get_usage.py u all --> usage for all trial users AND paid users for all time
# get_usage.py u all 2019-05 --> usage for all trial users AND paid users just for May 2019
# get_usage.py u trial --> usage for all trial users for all time
# get_usage.py u trial 2019-05 --> usage for all trial users just for May 2019
# get_usage.py u trial @paulhastings.com --> usage for Paul Hastings trial users for all time
# get_usage.py u trial @paulhastings.com 2019-05 --> usage for Paul Hastings trial users just for May 2019
# get_usage.py u lgc --> usage for Legalicity for all time
# get_usage.py u lgc 2019-05 --> usage for Legalicity just for May 2019
# get_usage.py u lgc yaroslav@legalicity.net --> usage for Legalicity's Yaroslav for all time
# Examples for Activity:
# get_usage.py a trial @paulhastings.com --> activity for Paul Hastings trial users for all time
# get_usage.py a trial @paulhastings.com 2019-05 --> activity for Paul Hastings trial users just for May 2019
# get_usage.py a lgc yaroslav@legalicity.net --> activity for Legalicity's Yaroslav for all time

##### HELPERS #####

def get_options(o_list):
    user, month = None, None
    # (1) check for email address
    for x in o_list:
        if re.match(EMAIL_PATTERN, x.lower()):
            user = x.lower()
            break
    # (2) check for month
    for y in o_list:
        try:
            datetime.strptime(y.lower(), '%Y-%m')
            month = y.lower()
            break
        except:
            pass # do nothing
    return user, month

##### MAIN #####

def run_usage(c_id, user=None, month=None):
    d = '{}/clients'.format(DIR)
    if c_id == 'all':
        # get usage for TRIAL users
        dd = '{}/{}/'.format(d, 'trial')
        users = sorted([name for name in os.listdir(dd) if os.path.isdir(os.path.join(dd, name))])
        t_n_s, t_n_u = print_usage('trial', users, user, month)
        print('-- {} -- TRIAL SEARCHES AND -- {} -- TRIAL UPDATES'.format(t_n_s, t_n_u))
        print(' ')
        # get usage for ALL PAYING clients
        clients = sorted([c for c in os.listdir(d)])
        clients.remove('lgc') # don't need to include our own usage
        clients.remove('trial') # already did trial users
        t_n = (0, 0)
        for client in clients:
            # try to get a list of users
            dd = '{}/{}/'.format(d, client)
            users = sorted([name for name in os.listdir(dd) if os.path.isdir(os.path.join(dd, name))])
            if users:
                t_n = tuple(map(sum, zip(t_n, print_usage(client, users, user, month))))
        print('-- {} -- PAID SEARCHES AND -- {} -- PAID UPDATES'.format(t_n[0], t_n[1]))
        print(' ')
    else:
        dd = '{}/{}/'.format(d, c_id)
        users = sorted([name for name in os.listdir(dd) if os.path.isdir(os.path.join(dd, name))])
        t_n_s, t_n_u = print_usage(c_id, users, user, month)
        print('-- {0} -- {2} SEARCHES AND -- {1} -- {2} UPDATES'.format(t_n_s, t_n_u, c_id.upper()))
        print(' ')

def print_usage(client, users, email, month):
    total_num_searches, total_num_updates = 0, 0
    print(client.upper())
    count = 0
    # go through each user for this client
    for u in users:
        if email and not u.endswith(email): continue
        # check if they have a usage.txt OR log.txt file
        f_name = 'usage' if client == 'trial' else 'log'
        if os.path.exists('{}/clients/{}/{}/{}.txt'.format(DIR, client, u, f_name)):
            # get all the lines in the usage file
            lines = [line.strip() for line in codecs.open('{}/clients/{}/{}/{}.txt'.format(DIR, client, u, f_name), 'r', 'utf-8')]
            if lines:
                d_s, d_u = {}, {}
                for l in lines:
                    d = l.split()[0]
                    if month and not d.startswith(month): continue
                    t = l.split()[1] if client == 'trial' else l.split()[2]
                    search_code = 'S' if client == 'trial' else '2'
                    if t == search_code:
                        d_s[d] = d_s[d] + 1 if d in d_s else 1
                    elif t == 'U': # same Update code for usage.txt & log.txt
                        d_u[d] = d_u[d] + 1 if d in d_u else 1
                if d_s or d_u:
                    # first, add up the total searches & updates
                    total_num_searches += sum(d_s.values())
                    total_num_updates += sum(d_u.values())
                    # then, create String summaries
                    x = []
                    for date in sorted(list(set(d_u.keys() + d_s.keys()))):
                        if date in d_s and date in d_u:
                            s = '{} (searches: {}, updates: {})'.format(date, d_s[date], d_u[date])
                        elif date in d_s:
                            s = '{} (searches: {})'.format(date, d_s[date])
                        else:
                            s = '{} (updates: {})'.format(date, d_u[date])
                        x.append(s)
                    count +=1
                    print('({}) {} : {}'.format(count, u, '; '.join(x)))
    print(' ')
    return total_num_searches, total_num_updates

def run_activity(c_id, user=None, month=None):
    # initialize
    d = '{}/clients/{}'.format(DIR, c_id)
    users = sorted([name for name in os.listdir(d) if os.path.isdir(os.path.join(d, name))])
    print('')
    num_active, num_inactive = 0, 0
    # go through all the users for this client organization, or just a particular user
    for u in users:
        if user and not u.endswith(user): continue
        # make sure log file exists
        if not os.path.exists('{}/{}/log.txt'.format(d, u)):
            print('{} : WRONG USER OR USER HAS NO LOG FILE'.format(u))
            print('')
            continue
        # get all the lines in the log file
        lines = [line.strip() for line in codecs.open('{}/{}/log.txt'.format(d, u), 'r', 'utf-8')]
        # make sure log file isn't empty or doesn't just have one line (account created)
        if not lines or len(lines) < 2:
            num_inactive +=1
            print('(X.{}) {} : NOT ACTIVE'.format(num_inactive, u))
            print('')
            continue
        # go through each line in the log file & record activity
        dates, activities = [], {}
        for l in lines:
            date = l.split()[0]
            if month and not date.startswith(month): continue
            if date not in dates: dates.append(date)
            code = l.split()[2]
            activities[code] = activities[code] + 1 if code in activities else 1
        # display the user's email address
        if not dates:
            print('{}'.format(u))
        else:
            num_active +=1
            print('({}) {}'.format(num_active, u))
            # display when the user has been active
            print('\tActive on: {}'.format('; '.join(dates)))
            # display what activity the user has been conducting
            a = []
            for c in CODES:
                if c in activities:
                    a.append('{} ({})'.format(CODE_NAMES[c], activities[c]))
            print('\tActivities: {}'.format('; '.join(a)))
        print('')

if '__main__' == __name__:
    try:
        # GET ACTION & CLIENT
        a = sys.argv[1].lower()
        c_id = sys.argv[2].lower()
        
        # usage (searches & updates, only for active users)
        if a == 'u':
            if c_id == 'trial' or c_id == 'all' or c_id in CLIENTS:
                # GET OPTIONS
                user, month = get_options(sys.argv[3:])
                # RUN
                run_usage(c_id, user, month)
            else:
                print("You have not selected a valid client! Try again.")
        # activity (various activity, for all users, including inactive ones)
        elif a == 'a':
            if c_id == 'trial' or c_id in CLIENTS:
                # GET OPTIONS
                user, month = get_options(sys.argv[3:])
                # RUN
                run_activity(c_id, user, month)
            else:
                print("You have not selected a valid client! Try again.")
        else:
            print("You have not selected a valid option! Try again.")
    except:
        print("There is an error! Try again.")
