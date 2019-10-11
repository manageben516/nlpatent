import sys, jwt, os

JWT_CLIENT_KEY = os.environ["JWT_CLIENT_KEY"]

##### HOW TO USE #####
# get_order_form_link.py [client ID]
## Example: get_order_form_link.py lgc

##### MAIN #####

def run(c_id):
    print('https://www.nlpatent.com/order/{}'.format(jwt.encode({'c_id': c_id}, JWT_CLIENT_KEY, algorithm='HS256')))

if '__main__' == __name__:
    try:
        run(sys.argv[1].lower())
    except Exception as e:
        print("There is an error! Try again: {}")

