 # -*- coding: utf-8 -*-
from gen_const import get_redis

if '__main__' == __name__:
    r = get_redis()
    p = '6843049'
    t = 'Systems and methods for harvesting fresh produce'
    a = 'Systems and methods for harvesting fresh produce using a produce harvesting apparatus wherein the method includes trimming the fresh produce and placing the trimmed produce into a container. The container is placed onto a transport device located on the produce harvesting apparatus. The container is then transported on the transport device to a wash station and it is washed at the wash station. The container may be shaken during transport after the wash station.'
    d = 20050118
    e = 'wash station;trimmed produce;container;load station;conveyor'

    r.hset(p, 't', t)
    r.hset(p, 'a', a)
    r.hset(p, 'd', d)
    r.hset(p, 'e', e)

    title = r.hget(p, 't')
    print("{}: {}".format(p, title))
    abstract = r.hget(p, 'a')
    print("{}".format(abstract))
    date = r.hget(p, 'd')
    print("{}: {} (type {})".format(p, date, type(date)))
    elements = r.hget(p, 'e').split(';')
    for x in elements:
        print("Element: {}".format(x))
    
    try:
        if p in r:
            print("[METHOD 1 WORKS]")
        else:
            print("[METHOD 1 DOESN'T WORK]")
    except:
        print("[METHOD 1 PRODUCES AN ERROR]")
    
    try:
        if r.exists(p):
            print("[METHOD 2 WORKS]")
        else:
            print("[METHOD 2 DOESN'T WORK]")
    except:
        print("[METHOD 2 PRODUCES AN ERROR]")

    r.hdel(p, 't') # delete title
    if r.hexists(p, 't'):
        print("[BAD] Title still exists after removing.")
    else:
        print("[GOOD] Title no longer exists after removing.")
    
    r.delete(p) # delete the hash

    try:
        if p in r:
            print("[METHOD 1 DOESN'T WORK]")
        else:
            print("[METHOD 1 WORKS]")
    except:
        print("[METHOD 1 PRODUCES AN ERROR]")
    
    try:
        if r.exists(p):
            print("[METHOD 2 DOESN'T WORK]")
        else:
            print("[METHOD 2 WORKS]")
    except:
        print("[METHOD 2 PRODUCES AN ERROR]")
    


