# -*- coding: utf-8 -*-
import os, sys, glob
from gen_const import DIR, CPC_PATH, DESCR_PATH, SENT_PATH, VEC_PATH, ELEM_PATH, TITLE_PATH, DATE_PATH, ABSTRACT_PATH, CPC_SECTIONS
from gen_const import get_redis, get_titles

def run_titles_and_cpc():
    r = get_redis() # get Redis
    # go through each mappings file
    for f_name in glob.glob('{}/{}/*'.format(DIR, TITLE_PATH)):
        titles = get_titles(f_name) # get the mappings
        cpc = os.path.basename(f_name).split('.')[0] # get the CPC subclass
        # go through every patent number in titles
        for p in titles:
            r.hset(p, 't', titles[p])
            r.hset(p, 'c', cpc)

if '__main__' == __name__:
    try:
        o = sys.argv[1] # option, e.g. 't' for Titles
        if o == 't':
            run_titles_and_cpc()
            print("DONE WITH TITLES & CPC SUBCLASSES")
        elif o == 'a':
            pass
        elif o == 'd':
            pass
        elif o == 'e':
            pass
        else:
            print("You have not selected a valid option! Try again.")
    except Exception as e:
        print("There is an error! {}".format(str(e)))