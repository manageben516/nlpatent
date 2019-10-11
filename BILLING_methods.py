 # -*- coding: utf-8 -*-
import os, sys, stripe, smtplib, codecs
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.mime.application import MIMEApplication
import BILLING_generate_usage as bgu
import BILLING_generate_receipt as bgr
import BILLING_generate_invoice as bgi
from gen_const import DIR, BILLING_PATH, BILLING_CLIENTS, BILLING_CLIENTS_TAX, CLIENTS_CURRENCY, CLIENTS_COST_SEARCH, CLIENTS_COST_UPDATE, CLIENTS_CONTACTS, CLIENTS_ADDRESSES, CLIENTS_INVOICING, CLIENTS_INVOICE_DUE_DATES, CLIENTS_INVOICE_ACTIVATION_FEE, BANK_ACCOUNT, COST_ACTIVATION
from gen_const import get_mongo_db


##### HOW TO USE ##############################################################
# Usage:		    BILLING_methods.py [date] u [c_id]
# Receipt:	        BILLING_methods.py [date] r [c_id] [num_searches(int)] [num_updates(int)]
# Invoice:	        BILLING_methods.py [date] i [c_id] [num_searches(int)] [num_updates(int)] [activation_fee(0 or 50)]
# Send Receipt: 	BILLING_methods.py [date] sr [c_id]
# Send Invoice: 	BILLING_methods.py [date] si [c_id]

# Usage + Receipt/Invoice   BILLING_methods.py [date]

##### CONSTANTS ###############################################################

stripe.api_key = os.environ["STRIPE_SECRET_KEY"]

##### HELPERS #################################################################

def get_payment_info(customer_id):
    customer = stripe.Customer.retrieve(customer_id)
    card = customer.sources.retrieve(customer.default_source)
    b = card.brand if 'brand' in card else ''
    return b, '****{}'.format(card.last4)

def reset_usage(c_id, emails):
    # go through each email address
    for e in emails:
        # set its MongoDB usage to zero
        usersDB.update_one({'email': e}, {'$set': {'num_searches': 0, 'num_updates': 0}})
        # overwrite usage.txt
        with codecs.open('{}/clients/{}/{}/usage.txt'.format(DIR, c_id, e), 'w', 'utf-8') as f:
            pass

###############################################################################

def get_usage(c_id, usersDB, m):
    d = {u['email']: (u['num_searches'], u['num_updates']) for u in usersDB.find({'client': c_id}) if u['num_searches'] > 0}
    if not d:
        print('No usage this month ({}) for client: {}'.format(m, c_id))
        return None, None
    try:
        # generate usage breakdown by individual user
        bgu.run(c_id, BILLING_CLIENTS[c_id], d, m, CLIENTS_COST_SEARCH[c_id], \
            CLIENTS_COST_UPDATE[c_id])
        # reset the number of searches & updates to zero
        reset_usage(c_id, d.keys())
    except:
        print("ERROR when generating usage breakdown; usage MAY HAVE been reset! Here's the saved usage:")
        for e in sorted(d): print(u'{} : {} searches, {} updates'.format(e, d[e][0], d[e][1]))
        return None, None
    return tuple(map(sum, zip(*d.values()))) # (total searches, total updates)

def get_receipt(c_id, usersDB, m, d, s, u):
    # get all the admins for this client organization
    a = [y for y in usersDB.find({'client': c_id}) if y['admin']]
    if not a:
        print('No admins for client: {}'.format(c_id))
        return
    # get the Stripe ID
    s_id = None
    for x in a:
        if 'stripe_id' in x:
            s_id = x['stripe_id']
            break
    if not s_id:
        print('No Stripe ID found for client: {}'.format(c_id))
        return
    # get the client's credit card info
    p_type, p_last4 = get_payment_info(s_id)
    # calculate amounts
    amt_usage = s*CLIENTS_COST_SEARCH[c_id] + u*CLIENTS_COST_UPDATE[c_id] # int
    amt_tax = float('{:,.2f}'.format(amt_usage*(BILLING_CLIENTS_TAX[c_id][1]/100.0))) if BILLING_CLIENTS_TAX[c_id][0] else 0.0 # float
    amt_total = amt_usage + amt_tax # float
    # generate Word & PDF receipt
    bgr.run(c_id, BILLING_CLIENTS[c_id], m, d, s, u, CLIENTS_COST_SEARCH[c_id], \
            CLIENTS_COST_UPDATE[c_id], BILLING_CLIENTS_TAX[c_id], amt_usage, amt_tax, \
            amt_total, p_type, p_last4, CLIENTS_CURRENCY[c_id])

def get_invoice(c_id, m, d, s, u, activation_fee=None):
    # calculate amounts for usage
    amt_usage = s*CLIENTS_COST_SEARCH[c_id] + u*CLIENTS_COST_UPDATE[c_id] # int
    amt_tax = float('{:,.2f}'.format(amt_usage*(BILLING_CLIENTS_TAX[c_id][1]/100.0))) if BILLING_CLIENTS_TAX[c_id][0] else 0.0 # float
    amt_total = amt_usage + amt_tax # float
    # calculate amounts including activation fee, if any
    if activation_fee: # int
        activation_fee_tax = float('{:,.2f}'.format(activation_fee*(BILLING_CLIENTS_TAX[c_id][1]/100.0))) if BILLING_CLIENTS_TAX[c_id][0] else 0.0 # float
        amt_total += activation_fee + activation_fee_tax # float
    else:
        activation_fee_tax = None
    # generate Word & PDF receipt
    bgi.run(c_id, BILLING_CLIENTS[c_id], m, d, s, u, CLIENTS_COST_SEARCH[c_id], \
            CLIENTS_COST_UPDATE[c_id], BILLING_CLIENTS_TAX[c_id], amt_usage, amt_tax, \
            amt_total, CLIENTS_CURRENCY[c_id], CLIENTS_ADDRESSES[c_id], \
            CLIENTS_INVOICE_DUE_DATES[c_id], activation_fee, activation_fee_tax, BANK_ACCOUNT[CLIENTS_CURRENCY[c_id]])

def get_all(usersDB, m, d):
    clients = list(BILLING_CLIENTS) # duplicate client list
    clients.remove('lgc') # remove 'lgc' from client list
    for c_id in clients: # go through each client
        t_s, t_u = get_usage(c_id, usersDB, m) # get total number of searches & updates
        if t_s: # check if usage isn't None
            if c_id in CLIENTS_INVOICING: # invoice
                a_f = COST_ACTIVATION if c_id in CLIENTS_INVOICE_ACTIVATION_FEE else None
                get_invoice(c_id, m, d, t_s, t_u, activation_fee=a_f)
            else: # receipt
                get_receipt(c_id, usersDB, m, d, t_s, t_u)

def send_email(c_id, m, email, invoice=False):
    # send the receipt by email
    t = 'invoice' if invoice else 'receipt'
    fromaddr = 'stephanie@legali.city'
    toaddr = email
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = 'NLPatent {} | {}'.format(t, m)
    body = '<p>Hello,</p>'
    body += '<p>Please find attached your NLPatent {} and summary of usage for month {}.</p>'.format(t, m)
    body += "<p>Let us know if you have any questions, and thanks again for using NLPatent!</p>"
    body += '<br>Best regards,<br>Stephanie<br>COO, Legalicity'
    msg.attach(MIMEText(body, 'html'))
    with open("{}/{}/{}_{}.pdf".format(BILLING_PATH, m, c_id, t), "rb") as f:
        opened_file = f.read()
    attached_file = MIMEApplication(opened_file)
    attached_file.add_header('content-disposition', 'attachment', filename = "{}_{}.pdf".format(c_id, t))
    msg.attach(attached_file)
    with open("{}/{}/{}_usage.pdf".format(BILLING_PATH, m, c_id), "rb") as f:
        opened_file = f.read()
    attached_file = MIMEApplication(opened_file)
    attached_file.add_header('content-disposition', 'attachment', filename = "{}_usage.pdf".format(c_id))
    msg.attach(attached_file)
    server = smtplib.SMTP('smtp.office365.com', 587)
    server.starttls()
    server.login(fromaddr, os.environ["EMAIL_PASSWORD"])
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

def send_emails(c_id, m, recipients, invoice=False):
    for e in recipients:
        send_email(c_id, m, e, invoice)
    print("Email successfully sent to: {}".format(c_id))

if '__main__' == __name__:
    try:
        # STANDARD
        usersDB = get_mongo_db()
        d = sys.argv[1] # day, e.g. "2019-03-31"
        m = d[:d.rfind('-')] # month, e.g. "2019-03""
        path = '{}/{}'.format(BILLING_PATH, m)
        if not os.path.exists(path): # make sure this folder exists
            os.makedirs(path)
        
        # ACTION & CLIENT ID
        if len(sys.argv) > 2:
            a = sys.argv[2].lower()
            c_id = sys.argv[3].lower()

        # OPTIONS
        if len(sys.argv) > 4: # if this is get receipt/invoice
            n_s, n_u = int(sys.argv[4]), int(sys.argv[5])
            if a == 'r':
                get_receipt(c_id, usersDB, m, d, n_s, n_u)
            elif a == 'i':
                a_f = None if int(sys.argv[6]) == 0 else int(sys.argv[6])
                get_invoice(c_id, m, d, n_s, n_u, activation_fee=a_f)
            else:
                print("You have not selected a valid option! Try again.")
        elif len(sys.argv) < 3: # if this is usage + receipt/invoice for ALL clients
            get_all(usersDB, m, d)
        else: # if this is get usage, or send receipt/invoice
            if a == 'u':
                get_usage(c_id, usersDB, m)
            elif a == 'sr':
                send_emails(c_id, m, CLIENTS_CONTACTS[c_id], invoice=False)
            elif a == 'si':
                send_emails(c_id, m, CLIENTS_CONTACTS[c_id], invoice=True)
            else:
                print("You have not selected a valid option! Try again.")
    except Exception as e:
        print("There is an error! {}".format(str(e)))


