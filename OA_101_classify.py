import codecs, re, pickle, warnings, pat_const
import numpy as np
from gen_const import DIR, DIR_101, HIGH_TECH_SECTIONS, LIFE_SCIENCES_SECTIONS, NUM_AT_RISK_WORDS

def run(description, cpc_section, c_id, email, p_n):
	# process description
	d = []
	for t in description.strip().replace('/', ' / ').replace('.', ' . ').replace(',', ' , ').replace(':', ' : ').replace(';', ' ; ').split():
	    x = re.sub("[\-\"\']", '', t).lower().strip() # remove BASIC punctuation & convert to lowercase
	    if len(x) < 3 or not x.isalpha() or x in pat_const.ALL: continue
	    d.append(x)
	input_text = ' '.join(d)

	# check which areas we need to go through
	areas = []
	if cpc_section in HIGH_TECH_SECTIONS: areas.append('high_tech')
	if cpc_section in LIFE_SCIENCES_SECTIONS: areas.append('life_sciences')

	# go through each selection
	for area in areas:
	    # load models
	    vectorizer = pickle.load(open('{}/{}/tfidf.pkl'.format(DIR_101, area), 'rb'))
	    Xgboost_clf = pickle.load(open('{}/{}/xgboost.pkl'.format(DIR_101, area), 'rb'))
	    # get word list
	    words = np.array(vectorizer.get_feature_names())
	    selected_index = np.load('{}/{}/selected_index.npy'.format(DIR_101, area))
	    words = words[selected_index]
	    badw_index = np.load('{}/{}/badw_list_freqdiff.npy'.format(DIR_101, area))
	    # get tfidf features
	    X_test = vectorizer.transform([input_text])
	    # load the selected index
	    X_test = X_test[:,selected_index]
	    with warnings.catch_warnings(): # ignore the warnings
	        warnings.simplefilter('ignore')
	        #y_pred = Xgboost_clf.predict(X_test) # result 1 or 0
	        prob = Xgboost_clf.predict_proba(X_test) # probability
	    # prediction result (0-rejected; 1-granted)
	    #prediction = str(y_pred)
	    # reject probability
	    p = int(round(prob[0][0]*100))
	    # grant probability
	    #g = str(prob[0][1])
	    # find the words exist in testing sample
	    nonzero_index = X_test[0].nonzero()[1]
	    # get the good/bad words in testing sample
	    sorted_index_p_0 = [i for i in badw_index if (i in nonzero_index)]
	    # display NUM_AT_RISK_WORDS words, e.g. maximum of 20
	    if NUM_AT_RISK_WORDS > len(sorted_index_p_0):
		    topword_index_bad = sorted_index_p_0
	    else:
		    topword_index_bad = sorted_index_p_0[:NUM_AT_RISK_WORDS]
	    # get the top at risk words
	    w = [str(words[i]) for i in topword_index_bad]
	    # save these results
	    with codecs.open('{}/clients/{}/{}/{}/101_{}.txt'.format(DIR, c_id, email, p_n, area), 'w', 'utf-8') as f:
	        f.write('{}:{}\n'.format(p, ';'.join(w)))
