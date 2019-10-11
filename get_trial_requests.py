import codecs
from gen_const import DIR

##### HOW TO USE #####
# get_trial_requests.py (no arguments)

##### MAIN #####

def display():
    # get the list of trial requests
    s = ['({}) {}'.format(i, x) for i, x in enumerate([l.strip() for l in codecs.open('{}/clients/trial/requests.txt'.format(DIR), 'r', 'utf-8')], 1)]
    # print the list on the screen
    print('\n'.join(s))

if '__main__' == __name__:
    display()
