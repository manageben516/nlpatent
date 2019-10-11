import os, time, random, string, codecs, redis
from datetime import datetime
from datetime import timedelta
from pytz import timezone
from dateutil.relativedelta import relativedelta
from pymongo import MongoClient

##### PATHS #####
DIR = "/legalicity/nlpatent"
CPC_PATH = "data/cpc"
DESCR_PATH = "data/cpc/descriptions"
SENT_PATH = "data/sentences"
VEC_PATH = "data/vectors"
ELEM_PATH = "data/elements"
TITLE_PATH = "data/titles"
DATE_PATH = "data/dates"
ABSTRACT_PATH = "data/abstracts"
BILLING_PATH = "/legalicity/nlpatent/billing"
DIR_101 = "/legalicity/nlpatent/data/101"

##### GENERAL #####
COST_ACTIVATION = 50 # $50.00 activation fee for new clients
MAX_PROJECTS = 100 # maximum number of projects a user can have
MAX_PRIOR_ART = 25 # maximum number of prior art results TO DISPLAY
MAX_PRIOR_ARTX = 10 # maximum number of prior art results TO DISPLAY
MAX_PA_CUTOFF = 500 # maximum number of prior art results TO EXTRACT
MAX_KEY_ELEMENTS = 5 # maximum number of key elements the user can specify
MAX_KNOWN_PRIOR_ART = 20 # maximum number of known prior art the user can specify
MAX_SAVED_PRIOR_ART = 200 # maximum number of results the user can save
MAX_RESULT_ELEMENTS = 16 # can tweak this as we go
MAX_TRIAL_SEARCHES = 20 # maximum number of searches a free trial user can perform
MIN_PERCENT_101 = 50 # minumum percentage likelihood for a s. 101 rejection
NUM_AT_RISK_WORDS = 10 # number of significant words to print for 101

HIGH_TECH_SECTIONS = ['A', 'B', 'D', 'E', 'F', 'G', 'H']
LIFE_SCIENCES_SECTIONS = ['A', 'C', 'G']

CPC_SUBCLASSES_101 = {'G06F', 'G06Q', 'G06T', 'G01N', 'G06K', 'G07F', 'G09B', 'G10L', 'H04L', \
'H04N', 'H04W', 'H04M', 'A61B', 'A61K', 'A61N', 'A63F', 'A01N', 'A01H', 'C12Q', 'C12N', 'C12P', 'C07K'}

CPC_SECTIONS = {'A': 'HUMAN NECESSITIES', 'B': 'OPERATIONS; TRANSPORTING', \
'C': 'CHEMISTRY; METALLURGY', 'D': 'TEXTILES; PAPER', 'E': 'FIXED CONSTRUCTIONS', \
'F': 'MECHANICAL ENGINEERING; LIGHTING; HEATING; WEAPONS; BLASTING', 'G': 'PHYSICS', \
'H': 'ELECTRICITY'}

# UPDATE these eventualy, e.g. add 'cpc_section', 'applicants'; remove input elements
RMV_FN_1 = ['chosen_subclasses', 'prior_art_results', 'result_elements', 'input_elements', 'input_elements_vectors'] 

# remove 'updated_result_elements', 'updated_results_previous
REMOVE_FILENAMES_2 = ['updated_result_elements', 'updated_results_input', 'updated_results_vectors', \
'updated_results_previous', 'updated_results_current', 'filtered_results', 'filtered_results_filters', \
'101_high_tech', '101_life_sciences']

REMOVE_FILENAMES_1 = RMV_FN_1 + REMOVE_FILENAMES_2

##### CLIENTS #####
CLIENTS = {'lgc': 'Legalicity', 'trial': 'Trial Account', 'mcc': 'McCarthy Tetrault', \
'oyw': 'Oyen Wiggs', 'bru': 'Brunet and Co', 'rob': 'ROBIC', 'bcf': 'BCF', 'blk': 'Blakes', \
'jsl': 'Sander Law', 'gow': 'Gowling WLG', 'bnj': 'Bennett Jones', 'dww': 'Deeth Williams Wall', \
'wbd': 'Womble Bond Dickinson', 'lul': 'Lululemon', 'mtt': 'Miller Thomson', 'rwd': 'Rowand LLP', \
'pck': 'PCK', 'mtr': 'Meteorcomm', 'win': 'Winston & Strawn LLP', 'sip': 'Seed IP', 'int': 'Intact Insurance', \
'fie': 'Field Law', 'phs': 'Paul Hastings LLP', 'csh': 'Cold Spring Harbor Laboratory', 'spy': 'Shopify', \
'bjf': 'Barta, Jones, & Foley'}

BILLING_CLIENTS = {'lgc': 'Legalicity', 'oyw': 'Oyen Wiggs', 'bru': 'Brunet and Co', \
'rob': 'ROBIC', 'bnj': 'Bennett Jones', 'blk': 'Blake, Cassels & Graydon LLP', \
'jsl': 'Sander Law', 'lul': 'Lululemon', 'dww': 'Deeth Williams Wall LLP', \
'mtt': 'Miller Thomson LLP', 'gow': 'Gowling WLG (Canada) LLP', 'mcc': 'McCarthy Tetrault LLP', \
'rwd': 'Rowand LLP', 'wbd': 'Womble Bond Dickinson', 'sip': 'Seed IP', 'int': 'Intact Insurance', \
'fie': 'Field Law', 'phs': 'Paul Hastings LLP', 'spy': 'Shopify', 'bjf': 'Barta, Jones, & Foley'}

CLIENTS_TAX_RATES = {'lgc': 1.13, 'trial': 1.0, 'mcc': 1.13, 'oyw': 1.05, 'bru': 1.13, \
'rob': 1.05, 'bcf': 1.05, 'blk': 1.13, 'jsl': 1.13, 'gow': 1.13, 'bnj': 1.13, \
'dww': 1.13, 'wbd': 1.0, 'lul': 1.05, 'mtt': 1.13, 'rwd': 1.13, 'pck': 1.13, 'mtr': 1.0, \
'win': 1.0, 'sip': 1.0, 'int': 1.13, 'fie': 1.05, 'phs': 1.0, 'csh': 1.0, 'spy': 1.13, \
'bjf': 1.0}

BILLING_CLIENTS_TAX = {'lgc': ('HST', 13), 'oyw': ('GST', 5), 'bru': ('HST', 13), \
'rob': ('GST', 5), 'bnj': ('HST', 13), 'blk': ('HST', 13), 'jsl': ('HST', 13), \
'lul': ('GST', 5), 'dww': ('HST', 13), 'mtt': ('HST', 13), 'gow': ('HST', 13), \
'mcc': ('HST', 13), 'rwd': ('HST', 13), 'wbd': (None, 0), 'mtr': (None, 0), \
'win': (None, 0), 'sip': (None, 0), 'int': ('HST', 13), 'fie': ('GST', 5), \
'phs': (None, 0), 'csh': (None, 0), 'spy': ('HST', 13), 'bjf': (None, 0)}

CLIENTS_CURRENCY = {'lgc': 'CAD', 'trial': 'CAD', 'mcc': 'CAD', 'oyw': 'CAD', 'bru': 'CAD', \
'rob': 'CAD', 'bcf': 'CAD', 'blk': 'CAD', 'jsl': 'CAD', 'gow': 'CAD', 'bnj': 'CAD', 'dww': 'CAD', \
'wbd': 'USD', 'lul': 'CAD', 'mtt': 'CAD', 'rwd': 'CAD', 'pck': 'CAD', 'mtr': 'USD', 'win': 'USD', \
'sip': 'USD', 'int': 'CAD', 'fie': 'CAD', 'phs': 'USD', 'csh': 'USD', 'spy': 'CAD', 'bjf': 'USD'}

CLIENTS_COST_SEARCH = {'lgc': 50, 'trial': 0, 'mcc': 20, 'oyw': 20, 'bru': 20, \
'rob': 20, 'bcf': 20, 'blk': 20, 'jsl': 20, 'gow': 20, 'bnj': 20, 'dww': 50, 'wbd': 50, \
'lul': 20, 'mtt': 20, 'rwd': 50, 'pck': 50, 'mtr': 30, 'win': 30, 'sip': 50, 'int': 50, \
'fie': 50, 'phs': 50, 'csh': 40, 'spy': 50, 'bjf': 50}

CLIENTS_COST_UPDATE = {'lgc': 10, 'trial': 0, 'mcc': 5, 'oyw': 5, 'bru': 5, \
'rob': 5, 'bcf': 5, 'blk': 5, 'jsl': 5, 'gow': 5, 'bnj': 5, 'dww': 10, 'wbd': 10, \
'lul': 5, 'mtt': 5, 'rwd': 10, 'pck': 10, 'mtr': 0, 'win': 0, 'sip': 10, 'int': 10, \
'fie': 10, 'phs': 10, 'csh': 0, 'spy': 10, 'bjf': 10}

CLIENTS_INVOICING = {'blk', 'dww', 'gow', 'mcc', 'mtt', 'fie', 'win', 'csh'}

CLIENTS_INVOICE_DUE_DATES = {'blk': 30, 'dww': 30, 'mtt': 30, 'gow': 45, 'mcc': 30, 'fie': 30}

CLIENTS_INVOICE_ACTIVATION_FEE = {'mcc', 'mtt', 'fie'} # who hasn't paid the Activation Fee yet

CLIENTS_ADDRESSES = {'blk': '199 Bay St., Suite 4000,\nToronto, ON, M5L 1A9', \
'dww': '150 York St., Suite 400,\nToronto, ON, M5H 3S5', \
'mtt': '295 Hagey Blvd., Suite 300,\nWaterloo, ON, N2L 6R5', \
'gow': '100 King St. W, Suite 1600,\nToronto, ON, M5X 1G5', \
'mcc': '66 Wellington St. W, Suite 5300,\nToronto, ON, M5K 1E6', \
'fie': '400-444 7 Ave. SW,\nCalgary, AB, T2P 0X8'}

CLIENTS_CONTACTS = {'lgc': ['yaroslav@legali.city'], \
'oyw': ['lchan@patentable.com'], \
'bru': ['rob@brunetco.com'], \
'rob': ['bourget@robic.com'], \
'bnj': ['simpsonk@bennettjones.com'], \
'blk': ['christopher.lindo@blakes.com'], \
'jsl': ['jennifer@sanderlaw.ca'], \
'lul': ['kimoore@lululemon.co'], \
'dww': ['jjannuska@dww.com'], \
'mtt': [], \
'gow': ['itpo@gowlingwlg.com', 'rick.kathuria@gowlingwlg.com'], \
'mcc': ['smaharaj@mccarthy.ca'], \
'rwd': ['frowand@rowandlaw.com'], \
'wbd': ['bill.koch@wbd-us.com'], \
'mtr': [], \
'win': [], \
'sip': ['andym@seedip.com'], \
'int': [], \
'fie': [], 'phs': [], 'spy': [], 'bjf': []}

CLIENTS_SUBSCRIPTION = {'mtr': (6, 150), 'win': (6, 150), 'csh': (12, 120)} # (duration in months, max number of searches)

##### ORDER FORM & INVOICING #####
BANK_ACCOUNT = {'CAD': ('09999', '003', '1016963'), 'USD': ('06032', '003', '4020467')}

##### INVOICING #####
HST_ACCOUNT_NUMBER = '765702725RT0001'

##### GET_USAGE #####
CODES = ['P', 'D', 'R', 'S', 'N', '1', '2', 'U', 'O', 'F', 'X', 'Y', 'M', 'Z', '3', 'E', 'L']
CODE_NAMES = {'P': 'new project created', 'D': 'project deleted', 'R': 'project renamed', \
'S': 'security setting enabled', 'N': 'security setting disabled', '1': 'Step 1 submission', \
'2': 'Step 2 submission', '3': 'Step 3 submission', 'U': 'update results', 'O': 'back to original results', \
'F': 'filter results', 'X': 'delete result', 'Y': 'save result', 'M': 'save result manually', 'Z': 'remove result', \
'E': 'email results', 'L': 'download results'}
EMAIL_PATTERN = '[^@]*@[^@]+\.[^@]+' # to detect '@xyz.com' & full email addresses

##### FUNCTIONS ################################################################################################

def generate_timestamp():
    try:
        tz = timezone('US/Eastern') # make sure to get the right timezone
        p_l = datetime.now(tz).strftime("%Y-%m-%d %I:%M%p")
    except: # just in case - not as good because doesn't take timezone into consideration
        p_l = time.strftime("%Y-%m-%d %I:%M%p")
    return p_l

def generate_daystamp():
    try:
        tz = timezone('US/Eastern') # make sure to get the right timezone
        p_l = datetime.now(tz).strftime("%Y-%m-%d")
    except: # just in case - not as good because doesn't take timezone into consideration
        p_l = time.strftime("%Y-%m-%d")
    return p_l

def get_forward_daystamp(c_id):
    # get current daystamp, 'YYYY-MM-DD'
    c = generate_daystamp()
    # calculate number of months in the future
    f = datetime.strptime(c, '%Y-%m-%d') + relativedelta(months=+CLIENTS_SUBSCRIPTION[c_id][0])
    # return String version of future daystamp
    return f.strftime("%Y-%m-%d")

def calculate_due_date(d, due_date):
    # d = String date, e.g. '2019-04-30'
    # due_date = int, e.g. 30 or 45
    x = datetime(int(d.split('-')[0]), int(d.split('-')[1]), int(d.split('-')[2])) # convert String to datetime
    y = x + timedelta(days=due_date) # add number of days
    return y.strftime("%Y-%m-%d") # convert back to String

def get_mongo_db():
    client = MongoClient("mongodb://legalicity:{0}@ds017896.mlab.com:17896/legalicity".format(os.environ["MONGO_PASSWORD"])) # connect to mLab's external MongoDB
    mDB = client.get_default_database() # get the default "Legalicity" database
    return mDB['users'] # get the 'users' collection

def get_redis():
    r = redis.Redis(host='redis')
    return r

def generate_random_password(num_chars):
    return ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(num_chars))

def get_dates(fName):
    return {line.strip().split('<D>')[0]: line.strip().split('<D>')[1] for line in codecs.open(fName, 'r', 'utf-8')}

def get_titles(fName):
    return {line.strip().split('<T>')[0]: line.strip().split('<T>')[1] for line in codecs.open(fName, 'r', 'utf-8')}

def get_abstracts(fName):
    return {line.strip().split('<A>')[0]: line.strip().split('<A>')[1] for line in codecs.open(fName, 'r', 'utf-8')}

def get_CPC_descriptions(fName):
    return {line.strip().split('<CPC>')[0]: line.strip().split('<CPC>')[1] for line in open(fName)}

def get_mapping(fName):
    return {l.strip().split(':')[0]: l.strip().split(':')[1].split(';') for l in codecs.open(fName, 'r', 'utf-8')}

def get_mapping_essential_elements(fName, pa):
    d = {}
    for l in codecs.open(fName, 'r', 'utf-8'):
        if len(d) >= len(pa): break
        x = l.strip().split(':')[0]
        if x in pa:
            d[x] = l.strip().split(':')[1].split(';')
    return d

def get_idf(fName):
    return {line.split(':')[0].strip(): float(line.split(':')[1].strip()) for line in codecs.open(fName, 'r', 'utf-8')}

def get_list(fName):
    return [line.strip() for line in codecs.open(fName, 'r', 'utf-8')]

def safe_remove(f_name):
    try:
        os.remove(f_name)
    except:
        pass # do nothing

def safe_remove_all(project_dir, f_names):
    for f_name in f_names: # go through each filename and try to safely remove it
        safe_remove('{}/{}.txt'.format(project_dir, f_name))

    