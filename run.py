import re, codecs, time, math, Levenshtein, pat_const 
import numpy as np
from gensim.models.keyedvectors import KeyedVectors
from gensim.models.wrappers import FastText
from gen_const import DIR, CPC_PATH, DESCR_PATH, SENT_PATH, VEC_PATH, ELEM_PATH, TITLE_PATH, DATE_PATH, ABSTRACT_PATH, CPC_SECTIONS, MAX_PRIOR_ART, MAX_SAVED_PRIOR_ART, MAX_PA_CUTOFF, MAX_KEY_ELEMENTS, MAX_RESULT_ELEMENTS
from gen_const import get_CPC_descriptions, get_titles, get_dates, get_abstracts, get_mapping, get_mapping_essential_elements, get_idf, get_list

##### HELPERS #####

def load_w2v_words(section):
    w2v = KeyedVectors.load("{}/{}/{}_w2v_{}_words-normed".format(DIR, VEC_PATH, section, 'SG'), mmap='r')
    w2v.vectors_norm = w2v.vectors
    return w2v

def save_essential_elements(tf, idf, oov_vecs, w2v, num_words, dim, c_id, email, project_name):
    # tf = dict of n-grams & their freqs; idf = dict of oov WORDS & their calculated idf
    # go through each n-gram; multiply: normalized freq of n-gram * length of n-gram * avg idf of n-gram
    newDict = {ng: (tf[ng]/num_words) * len(ng.split()) * np.mean([idf[x] for x in ng.split()]) for ng in tf}
    elems = []
    p50 = np.percentile(newDict.values(), 50) # calculate 50th percentile
    # open the write files
    f_e = codecs.open('{}/clients/{}/{}/{}/input_elements.txt'.format(DIR, c_id, email, project_name), 'w', 'utf-8')
    f_v = codecs.open('{}/clients/{}/{}/{}/input_elements_vectors.txt'.format(DIR, c_id, email, project_name), 'w', 'utf-8')
    for n in sorted(newDict, key=newDict.get, reverse=True):
        if len(elems) >= 3: # get AT LEAST 3 essential elements
            if newDict[n] < p50 or len(elems) >= MAX_KEY_ELEMENTS: break # keep it at max X elements!
        # check if this element is disqualified (for various reasons - see helper method)
        if disqualify_element(tf, n, elems): continue
        # save the text & vector for this essential element
        f_e.write(u'{}\n'.format(n))
        x = np.zeros(dim, dtype=np.float32) # initialize an empty vector
        for w in n.split(): # calculate the vector for this n-gram
            x = (x + w2v[w]) if w in w2v else (x + oov_vecs[w]) # SUM of each word in n-gram
        np.savetxt(f_v, x, newline=' ', comments='')
        f_v.write('\n')
        elems.append(n)
    f_e.close()
    f_v.close()

def save_essential_elements_manual(section, elems, oov_vecs, w2v, ft, dim, c_id, email, project_name):
    # open the write files
    f_e = codecs.open('{}/clients/{}/{}/{}/input_elements.txt'.format(DIR, c_id, email, project_name), 'w', 'utf-8')
    f_v = codecs.open('{}/clients/{}/{}/{}/input_elements_vectors.txt'.format(DIR, c_id, email, project_name), 'w', 'utf-8')
    count = 0
    for e in elems:
        count +=1
        x = np.zeros(dim, dtype=np.float32) # initialize an empty vector
        for t in elems[e].split():
            if t in w2v:
                x += w2v[t]
            elif t in oov_vecs:
                x += oov_vecs[t]
            else:
                if ft == None:
                    ft = FastText.load("{}/{}/{}_FT_{}_words-normed".format(DIR, VEC_PATH, section, 'SG'), mmap='r')
                try:
                    c_v = get_closest_vector(w2v, ft, t) # get an estimated vector for this OOV term
                except:  # VERY RARE case when no vector for word!
                    return {'ELEMENT_ERROR': 'Please rephrase this element, preferably without "{}".'.format(t), 'ELEMENT_NUMBER': count}
                x += c_v
                oov_vecs[t] = c_v # keep track of OOV vectors
        # save the text & vector for this essential element
        f_e.write(u'{}\n'.format(e))
        np.savetxt(f_v, x, newline=' ', comments='')
        f_v.write('\n')
    f_e.close()
    f_v.close()
    return {}

def check_manual_elements(key_elements):
    # key_elements = list of Strings entered by the user
    d_elems, already_seen, count = {}, set(), 0
    for e in key_elements: # go through each key element
        count +=1
        # make sure no duplicates!
        if e in already_seen:
            return True, {'ELEMENT_ERROR': 'This element is a duplicate. Please enter original elements.', 'ELEMENT_NUMBER': count}
        else:
            already_seen.add(e)
        s = e.strip().replace('/', ' / ').replace('.', ' . ').replace(',', ' , ').replace(':', ' : ').replace(';', ' ; ').split()
        if len(s) > 5:
            return True, {'ELEMENT_ERROR': 'This element is too long. Please keep it to 5 words or less.', 'ELEMENT_NUMBER': count}
        temp = []
        for t in s:
            x = re.sub("[\-\"\']", '', t).lower().strip() # remove BASIC punctuation & convert to lowercase
            if len(x) < 3 or not x.isalpha() or x in pat_const.ELEMENTS: continue
            temp.append(x)
        if len(temp) / float(len(s)) < 0.6:
            return True, {'ELEMENT_ERROR': 'This element is too vague. Please try again.', 'ELEMENT_NUMBER': count}
        d_elems[e] = ' '.join(temp)

    return False, d_elems

def check_and_save_elements(key_elements, section, c_id, email, project_name):
    # key_elements = list of Strings entered by the user
    d_elems, already_seen, count = {}, set(), 0
    for e in key_elements: # go through each key element
        count +=1
        # make sure no duplicates!
        if e in already_seen:
            return True, {'ELEMENT_ERROR': 'This element is a duplicate. Please enter original elements.', 'ELEMENT_NUMBER': count}, None
        else:
            already_seen.add(e)
        s = e.strip().replace('/', ' / ').replace('.', ' . ').replace(',', ' , ').replace(':', ' : ').replace(';', ' ; ').split()
        if len(s) > 5:
            return True, {'ELEMENT_ERROR': 'This element is too long. Please keep it to 5 words or less.', 'ELEMENT_NUMBER': count}, None
        temp = []
        for t in s:
            x = re.sub("[\-\"\']", '', t).lower().strip() # remove BASIC punctuation & convert to lowercase
            if len(x) < 3 or not x.isalpha() or x in pat_const.ELEMENTS: continue
            temp.append(x)
        if len(temp) / float(len(s)) < 0.6:
            return True, {'ELEMENT_ERROR': 'This element is too vague. Please try again.', 'ELEMENT_NUMBER': count}, None
        d_elems[e] = ' '.join(temp)

    w2v = KeyedVectors.load("{}/{}/{}_w2v_{}_words-normed".format(DIR, VEC_PATH, section, 'SG'), mmap='r')
    w2v.vectors_norm = w2v.vectors
    err = save_essential_elements_manual(section, d_elems, {}, w2v, None, 300, c_id, email, project_name)
    if err:
        return True, err, w2v
    else:
        return False, d_elems.keys(), w2v

def disqualify_element(tf, n, elems):
    # check if freq is too low or length is too short or length is too long or it subsumes/is subsumed by any existing element
    if tf[n] <= 1 or len(n.split()) > 5 or (len(n.split()) == 1 and len(elems) >= 5):
        return True
    x = set(n.split()) # make a set out of the input element
    for e in elems:
         if n in e or e in n: return True
         y = set(e.split()) # make a set out of each element already added
         # handle tricky case where elems are similar enough but not subsumed by each other
         # i.e. fraction of words is the same: 2/3, 3/4, and 3/5
         if len(x.intersection(y)) / float(max(len(x), len(y))) >= 0.6: return True
    return False

def average_results(r1, r2):
    d1, d2 = {x: y for x, y in r1}, {x: y for x, y in r2}
    return [(x, (d1[x]+d2[x])/2.0) for x in d1]

def save_prior_art(pa, c_id, email, project_name):
    with codecs.open('{}/clients/{}/{}/{}/prior_art_results.txt'.format(DIR, c_id, email, project_name), 'w') as f_out:
        for p_n, cpc in pa:
            f_out.write('{}:{}\n'.format(p_n, cpc)) # record patent number AND subclass it's found in

def get_most_similar(model, w, n):
    d = {x: model.similarity(x, w) for x in model.wv.vocab}
    return [(x, d[x]) for x in sorted(d, key=d.get, reverse=True)[:n]]

def get_closest_vector_and_idf(w2v, ft, idf, t):
    # get the top 10 most similar words to t
    #ms = get_most_similar(ft, t, 10)
    ms = ft.most_similar(t, topn=10)
    # narrow down to only the closest matches
    matches, top_s, prev_s = [ms[0][0]], ms[0][1], ms[0][1]
    for (w, s) in ms[1:]:
        if s > (prev_s - 0.03) and s > (top_s - 0.1):
            matches.append(w)
            prev_s = s
        else:
            break
    # average out all matches vectors & idfs
    return np.mean([w2v[m] for m in matches], axis=0), np.mean([idf[m] for m in matches])

def get_closest_vector(w2v, ft, t):
    #t1 = time.time()
    # get the top 10 most similar words to t
    #ms = get_most_similar(ft, t, 10)
    ms = ft.most_similar(t, topn=10)
    # narrow down to only the closest matches
    matches, top_s, prev_s = [ms[0][0]], ms[0][1], ms[0][1]
    for (w, s) in ms[1:]:
        if s > (prev_s - 0.03) and s > (top_s - 0.1):
            matches.append(w)
            prev_s = s
        else:
            break
    # average out all matches vectors
    #t2 = time.time()
    #with codecs.open('{}/time2run.txt'.format(DIR), 'a', 'utf-8') as f_time:
    #    f_time.write(u"---TIME to get closest vector for '{}': ".format(t) + '%.2f' % (t2-t1) + " seconds.\n")
    return np.mean([w2v[m] for m in matches], axis=0)

def get_vector(element, w2v, w2v_oov):
    n = np.zeros(300, dtype=np.float32) # initialize an empty vector
    for e in element.split():
        if e in w2v:
            n += w2v[e]
        elif e in w2v_oov:
            n += w2v_oov[e]
        # otherwise don't add anything; so it could return empty vector!
    return n

def add_result_to_saved(pat_num, cpc_subclass, c_id, email, project_name):
    pa_saved = read_prior_art('{}/clients/{}/{}/{}/prior_art_saved.txt'.format(DIR, c_id, email, project_name))
    if len(pa_saved) >= MAX_SAVED_PRIOR_ART:
        return {'manual_saved_result': 'You cannot save more than {} results.'.format(MAX_SAVED_PRIOR_ART)}
    if pat_num in [x[0] for x in pa_saved]:
        return {'manual_saved_result': 'This has already been saved.'}    
    with codecs.open('{}/clients/{}/{}/{}/prior_art_saved.txt'.format(DIR, c_id, email, project_name), 'a', 'utf-8') as f_out:
        f_out.write('{}:{}\n'.format(pat_num, cpc_subclass))
    return False

def add_result_to_saved_manual(result, c_id, email, project_name):
    allowed_art = {'7654321': 'A47L', '20116543210': 'D06F'} # TEMPORARY - REMOVE LATER!
    r = result.encode('ascii').translate(None, "US/,") # leave only the number
    pa_known = get_list('{}/clients/{}/{}/{}/known_prior_art.txt'.format(DIR, c_id, email, project_name))
    pa_saved = read_prior_art('{}/clients/{}/{}/{}/prior_art_saved.txt'.format(DIR, c_id, email, project_name))
    if len(pa_saved) >= MAX_SAVED_PRIOR_ART:
        return {'manual_saved_result': 'You cannot save more than {} results.'.format(MAX_SAVED_PRIOR_ART)}
    if r in pa_known:
        return {'manual_saved_result': 'This is already in the known prior art.'}
    if r in [x[0] for x in pa_saved]:
        return {'manual_saved_result': 'This has already been saved.'}
    if r not in allowed_art:
        return {'manual_saved_result': 'This was not found in our database.'} # TEMPORARY - CHANGE THIS TO CHECKING IN REDIS
    with codecs.open('{}/clients/{}/{}/{}/prior_art_saved.txt'.format(DIR, c_id, email, project_name), 'a', 'utf-8') as f_out:
        f_out.write('{}:{}\n'.format(r, allowed_art[r])) # TEMPORARY - CHANGE THIS TO LOOK UP CPC SUBCLASS IN REDIS
    return False

def remove_result_from_saved(pat_num, c_id, email, project_name):
    pa_saved = read_prior_art('{}/clients/{}/{}/{}/prior_art_saved.txt'.format(DIR, c_id, email, project_name))
    try:
        saved_set = set(list(zip(*pa_saved)[0])) # error when pa_saved=[]
    except:
        saved_set = set()
    if pat_num in saved_set:
        with codecs.open('{}/clients/{}/{}/{}/prior_art_saved.txt'.format(DIR, c_id, email, project_name), 'w', 'utf-8') as f_out:
            for p, c in pa_saved:
                if p != pat_num: f_out.write('{}:{}\n'.format(p, c))
        return False
    else:
       return True

def add_result_to_deleted(pat_num, cpc_subclass, c_id, email, project_name):
    pa_deleted = read_prior_art('{}/clients/{}/{}/{}/prior_art_deleted.txt'.format(DIR, c_id, email, project_name))
    try:
        deleted_set = set(list(zip(*pa_deleted)[0])) # error when pa_deleted=[]
    except:
        deleted_set = set()
    if pat_num in deleted_set:
        return True
    else:
        with codecs.open('{}/clients/{}/{}/{}/prior_art_deleted.txt'.format(DIR, c_id, email, project_name), 'a', 'utf-8') as f_out:
            f_out.write('{}:{}\n'.format(pat_num, cpc_subclass))
        return False

def check_deleted_prior_art(pa, c_id, email, project_name):
    pa_deleted = read_prior_art('{}/clients/{}/{}/{}/prior_art_deleted.txt'.format(DIR, c_id, email, project_name))
    if pa_deleted:
        return [x for x in pa if x[0] not in set(list(zip(*pa_deleted)[0]))]
    else:
        return pa

def format_prior_art(pa, check_saved=False, pa_saved=[]):
    results, titles = [], {}
    if check_saved:
        try:
            saved_set = set(list(zip(*pa_saved)[0])) # error when pa_saved=[]
        except:
            saved_set = set()
        for p, c in pa:
            if c not in titles: titles[c] = get_titles('{}/{}/{}.txt'.format(DIR, TITLE_PATH, c))
            s = 1 if p in saved_set else 0
            t = titles[c][p] if p in titles[c] else 'NO TITLE AVAILABLE'
            results.append({'p': 'US{}'.format(p), 'c': c, 't': t, 's': s})
    else:
        for p, c in pa:
            if c not in titles: titles[c] = get_titles('{}/{}/{}.txt'.format(DIR, TITLE_PATH, c))
            t = titles[c][p] if p in titles[c] else 'NO TITLE AVAILABLE' # REMOVE THIS LATER
            results.append({'p': 'US{}'.format(p), 'c': c, 't': t}) # REMOVE THIS LATER
            #results.append({'p': 'US{}'.format(p), 'c': c, 't': titles[c][p]})
    return results

def format_prior_art_updated(pa, pa_saved):
    results, titles = [], {}
    try:
        saved_set = set(list(zip(*pa_saved)[0])) # error when pa_saved=[]
    except:
        saved_set = set()
    for p, c, x in pa:
        if c not in titles: titles[c] = get_titles('{}/{}/{}.txt'.format(DIR, TITLE_PATH, c))
        s = 1 if p in saved_set else 0
        t = titles[c][p] if p in titles[c] else 'NO TITLE AVAILABLE'
        results.append({'p': 'US{}'.format(p), 'c': c, 't': t, 's': s, 'x': x})
    return results

def save_filtered_results(filtered_results, c_id, email, project_name):
    with codecs.open('{}/clients/{}/{}/{}/filtered_results.txt'.format(DIR, c_id, email, project_name), 'w', 'utf-8') as f_r, codecs.open('{}/clients/{}/{}/{}/filtered_results_filters.txt'.format(DIR, c_id, email, project_name), 'w', 'utf-8') as f_f:
        # (1) save just the results - remove 'US' from start of patent number!
        f_r.write('\n'.join(['{}:{}'.format(r['p'][2:], r['c']) for r in filtered_results])+'\n')
        # (2) save just the filters separately - leave 'US' at start of patent number!
        for r in filtered_results:
            s = '{}:'.format(r['p']) # add the patent number
            s = s+','.join(r['k']) if 'k' in r else s+'_' # add any key elements
            s = s+'@'+','.join(r['r']) if 'r' in r else s+'@_' # add any result elements
            s = s+'@'+r['d'] if 'd' in r else s+'@_' # add the date, if there is one
            f_f.write('{}\n'.format(s))


def save_filtered_resultsX(filtered_results, c_id, email, project_name):
    with codecs.open('{}/clients/{}/{}/{}/filtered_results.txt'.format(DIR, c_id, email, project_name), 'w', 'utf-8') as f_r, codecs.open('{}/clients/{}/{}/{}/filtered_results_filters.txt'.format(DIR, c_id, email, project_name), 'w', 'utf-8') as f_f:
        # (1) save just the results - remove 'US' from start of patent number!
        f_r.write('\n'.join(['{}:{}'.format(r['p'][2:], r['c']) for r in filtered_results])+'\n')
        # (2) save just the filters separately - leave 'US' at start of patent number!
        for r in filtered_results:
            s = '{}:'.format(r['p']) # add the patent number
            s = s+','.join(r['k']) if 'k' in r else s+'_' # add any key elements
            s = s+'@'+','.join(r['r']) if 'r' in r else s+'@_' # add any result elements
            s = s+'@'+r['d'] if 'd' in r else s+'@_' # add the date, if there is one
            s = s+'@'+r['a'] if 'a' in r else s+'@_' # add the applicant, if there is one
            f_f.write('{}\n'.format(s))

def check_input_for_update_results(input_saved_pa, c_id, email, project_name):
    input_saved_previous = read_prior_art('{}/clients/{}/{}/{}/updated_results_input.txt'.format(DIR, c_id, email, project_name))
    return [(x, y) for x, y in input_saved_pa if x not in zip(*input_saved_previous)[0]]

def read_prior_art(fName):
    return [(l.strip().split(':')[0], l.strip().split(':')[1]) for l in codecs.open(fName, 'r', 'utf-8')]

def read_prior_art_minus_deleted(f, c_id, email, project_name):
    pa = read_prior_art('{}/clients/{}/{}/{}/{}.txt'.format(DIR, c_id, email, project_name, f))
    pa_deleted = read_prior_art('{}/clients/{}/{}/{}/prior_art_deleted.txt'.format(DIR, c_id, email, project_name))
    if pa_deleted:
        return [(x, y) for x, y in pa if x not in set(list(zip(*pa_deleted)[0]))]
    else:
        return pa

def read_prior_art_updated_minus_deleted(f, c_id, email, project_name):
    pa = [(l.strip().split(':')[0], l.strip().split(':')[1], l.strip().split(':')[2]) for l in codecs.open('{}/clients/{}/{}/{}/{}.txt'.format(DIR, c_id, email, project_name, f), 'r', 'utf-8')]
    pa_deleted = read_prior_art('{}/clients/{}/{}/{}/prior_art_deleted.txt'.format(DIR, c_id, email, project_name))
    if pa_deleted:
        return [x for x in pa if x[0] not in set(list(zip(*pa_deleted)[0]))]
    else:
        return pa

def cos(v1, v2):
    return np.dot(v1, v2) / np.sqrt(np.dot(v1, v1) * np.dot(v2, v2))

##### SECONDARY #####

def check_known_prior_art(input_art):
    allowed_art = ['1234567', '20040123456'] # TEMPORARY - REMOVE LATER!
    duplicates, errors, known_art, count = set(), {}, [], 0
    # go through each input patent/publication number
    for a in input_art:
        count +=1
        x = a.encode('ascii').translate(None, "US/,") # leave only the number
        if x in duplicates: # first, check if it's a duplicate
            errors['patent_{}'.format(count)] = 'This is a duplicate entry.'
            continue
        elif x not in allowed_art: # TEMPORARY - CHANGE THIS TO CHECKING IN REDIS
            errors['patent_{}'.format(count)] = 'This was not found in our database.'
        else:
            known_art.append(x)
        duplicates.add(x)
    return errors if errors else known_art

def get_term_frequencies(description):
    tf, num_words  = {}, 0.0
    # go through all tokens & build a lexicon dict w/ unique words as keys & tf as values
    for t in description.strip().replace('/', ' / ').replace('.', ' . ').replace(',', ' , ').replace(':', ' : ').replace(';', ' ; ').split():
        x = re.sub("[\-\"\']", '', t).lower().strip() # remove BASIC punctuation & convert to lowercase
        if len(x) < 3 or not x.isalpha() or x in pat_const.ELEMENTS: continue
        num_words += 1.0
        tf[x] = tf[x] + 1.0 if x in tf else 1.0
    return tf, num_words
    
def step_1_submit(tf, num_words, section, c_id, email, project_name):
    idf = get_idf('{}/{}/{}_idf.txt'.format(DIR, SENT_PATH, section)) # dict
    # read in the word vectors for this section
    w2v = KeyedVectors.load("{}/{}/{}_w2v_{}_words-normed".format(DIR, VEC_PATH, section, 'SG'), mmap='r')
    w2v.vectors_norm = w2v.vectors
    dim, ft = 300, None
    # go through all dict keys (unique words) & make a doc vector
    # L2 normalization (divide by this, instead of the sum)
    L2_norm = math.sqrt(sum(i*i for i in tf.values()))
    # calculate the vector for this patent
    num_oov, max_oov, n = 0, 5, np.zeros(dim, dtype=np.float32) # initialize an empty vector
    for t in sorted(tf, key=tf.get, reverse=True): # go through each unique word/token in this patent document
        if t in w2v:
            n += w2v[t]*(tf[t]/L2_norm)*idf[t]
        else:
            # handle OOV words here
            # check if this OOV word isn't significant, or if there are too many OOV words
            if tf[t]/num_words < 0.05 or num_oov >= max_oov: continue
            if not ft:
                ft = FastText.load("{}/{}/{}_FT_{}_words-normed".format(DIR, VEC_PATH, section, 'SG'), mmap='r')
            try:
                c_v, c_idf = get_closest_vector_and_idf(w2v, ft, idf, t) # get an estimated vector & idf score for this OOV term
            except:  # VERY RARE case when no vector for word!
                continue
            n += c_v*(tf[t]/L2_norm)*c_idf
            num_oov +=1 # keep track of number of OOV words, so it doesn't exceed max_oov (ex. 5)
    # save the input doc vector
    np.savetxt('{}/clients/{}/{}/{}/input_vector.txt'.format(DIR, c_id, email, project_name), n, newline=' ', comments='')
    # save the CPC section
    with codecs.open('{}/clients/{}/{}/{}/cpc_section.txt'.format(DIR, c_id, email, project_name), 'w', 'utf-8') as f_out:
        f_out.write(section)
    # generate & save the CPC classification results
    generate_and_save_CPC_results(n, section, c_id, email, project_name)

def generate_and_save_CPC_results(v, section, c_id, email, project_name):
    # read in the subclass vectors for this SECTION
    w2v = KeyedVectors.load_word2vec_format("{}/{}/{}_w2v_{}_subclasses.bin".format(DIR, VEC_PATH, section, 'SG'), binary=True)
    # read in the description vectors for this SECTION
    w2v_d = KeyedVectors.load_word2vec_format("{}/{}/{}_w2v_{}_subclasses_d.bin".format(DIR, DESCR_PATH, section, 'SG'), binary=True)
    results, results_d = w2v.similar_by_vector(v, topn=len(w2v.wv.vocab)), w2v_d.similar_by_vector(v, topn=len(w2v_d.wv.vocab))
    # categorize by SUBCLASS of this section
    with open('{}/clients/{}/{}/{}/input_subclasses.txt'.format(DIR, c_id, email, project_name), 'w') as f_out:
        f_out.write('\n'.join(['{}:{}'.format(z[0], '{0:.0%}'.format(z[1])) for z in sorted(average_results(results, results_d), key=lambda y: y[1], reverse=True)]))

def step_1_submitX(tf, num_words, known_prior_art, c_id, email, project_name):
    dim, num_oov, max_oov, vectors = 300, 0, 5, {}
    for section in CPC_SECTIONS:
        # load the inverse document frequencies
        idf = get_idf('{}/{}/{}_idf.txt'.format(DIR, SENT_PATH, section)) # dict
        # read in the word vectors for this section
        w2v = KeyedVectors.load("{}/{}/{}_w2v_{}_words-normed".format(DIR, VEC_PATH, section, 'SG'), mmap='r')
        w2v.vectors_norm = w2v.vectors
        ft = None
        # go through all dict keys (unique words) & make a doc vector
        # L2 normalization (divide by this, instead of the sum)
        L2_norm = math.sqrt(sum(i*i for i in tf.values()))
        # calculate the vector for this patent
        n = np.zeros(dim, dtype=np.float32) # initialize an empty vector
        for t in sorted(tf, key=tf.get, reverse=True): # go through each unique word/token in this patent document
            if t in w2v:
                n += w2v[t]*(tf[t]/L2_norm)*idf[t]
            else:
                # handle OOV words here
                # check if this OOV word isn't significant, or if there are too many OOV words
                if tf[t]/num_words < 0.05 or num_oov >= max_oov: continue
                if not ft:
                    ft = FastText.load("{}/{}/{}_FT_{}_words-normed".format(DIR, VEC_PATH, section, 'SG'), mmap='r')
                try:
                    c_v, c_idf = get_closest_vector_and_idf(w2v, ft, idf, t) # get an estimated vector & idf score for this OOV term
                except:  # VERY RARE case when no vector for word!
                    continue
                n += c_v*(tf[t]/L2_norm)*c_idf
                num_oov +=1 # keep track of number of OOV words, so it doesn't exceed max_oov (ex. 5)
        # save the input doc vector
        vectors[section] = n
        np.savetxt('{}/clients/{}/{}/{}/input_vector_{}.txt'.format(DIR, c_id, email, project_name, section), n, newline=' ', comments='')
        count +=1
    # generate & save the CPC classification results
    generate_and_save_CPC_resultsX(vectors, known_prior_art, c_id, email, project_name)

def generate_and_save_CPC_resultsX(vectors, known_prior_art, c_id, email, project_name):
    final_results = []
    for section in vectors:
        # read in the subclass vectors for this SECTION
        w2v = KeyedVectors.load_word2vec_format("{}/{}/{}_w2v_{}_subclasses.bin".format(DIR, VEC_PATH, section, 'SG'), binary=True)
        # read in the description vectors for this SECTION
        w2v_d = KeyedVectors.load_word2vec_format("{}/{}/{}_w2v_{}_subclasses_d.bin".format(DIR, DESCR_PATH, section, 'SG'), binary=True)
        # categorize by SUBCLASS of this section
        results, results_d = w2v.similar_by_vector(vectors[section], topn=len(w2v.wv.vocab)), w2v_d.similar_by_vector(vectors[section], topn=len(w2v_d.wv.vocab))
        final_results += average_results(results, results_d)
    with open('{}/clients/{}/{}/{}/input_subclasses.txt'.format(DIR, c_id, email, project_name), 'w') as f_out:
        f_out.write('\n'.join(['{}:{}'.format(z[0], '{0:.0%}'.format(z[1])) for z in sorted(final_results, key=lambda y: y[1], reverse=True)]))

# returns a list of tuples, e.g. ('A47L', '94%')
def get_all_CPC_subclasses(c_id, email, project_name):
    return [(l.strip().split(':')[0], l.strip().split(':')[1]) for l in codecs.open('{}/clients/{}/{}/{}/input_subclasses.txt'.format(DIR, c_id, email, project_name), 'r', 'utf-8')]

def get_CPC_classes(c_id, email, project_name):
    cpc_descr = get_CPC_descriptions('{}/{}/cpc-descriptions.txt'.format(DIR, CPC_PATH))
    cpc_subclasses = get_all_CPC_subclasses(c_id, email, project_name)
    cl, options = set(), []
    for c, p in cpc_subclasses:
        if c[:-1] not in cl:
            options.append({'n': c[:-1], 'p': p, 't': cpc_descr[c[:-1]]})
            cl.add(c[:-1])
    return options

def get_CPC_classesX(section, c_id, email, project_name):
    cpc_descr = get_CPC_descriptions('{}/{}/cpc-descriptions.txt'.format(DIR, CPC_PATH))
    cpc_subclasses = get_all_CPC_subclasses(c_id, email, project_name)
    cl, options = set(), []
    for c, p in cpc_subclasses:
        if c[0] != section: continue # skip any subclasses NOT from the selected CPC section
        if c[:-1] not in cl:
            options.append({'n': c[:-1], 'p': p, 't': cpc_descr[c[:-1]]})
            cl.add(c[:-1])
    return options

def get_CPC_subclasses(cpc_classes, c_id, email, project_name):
    cpc_descr = get_CPC_descriptions('{}/{}/cpc-descriptions.txt'.format(DIR, CPC_PATH))
    cpc_subclasses = get_all_CPC_subclasses(c_id, email, project_name)
    options = [{'n': c, 'p': p, 't': cpc_descr[c]} for c, p in cpc_subclasses if c[:-1] in cpc_classes]
    return options

def save_chosen_subclasses(cpc_subclasses, c_id, email, project_name):
    with open('{}/clients/{}/{}/{}/chosen_subclasses.txt'.format(DIR, c_id, email, project_name), 'w') as f_out:
        f_out.write('\n'.join(cpc_subclasses))

def get_prior_art(cpc_subclasses, c_id, email, project_name, priority_date):
    results_pa, results_cpc, v = {}, {}, np.loadtxt('{}/clients/{}/{}/{}/input_vector.txt'.format(DIR, c_id, email, project_name), dtype=np.float32)
    dates = {} # this is for filtering by priority date
    # go through each chosen subclass
    for cpc in cpc_subclasses:
        if priority_date > -1: dates[cpc] = get_dates('{}/{}/{}.txt'.format(DIR, DATE_PATH, cpc))
        # read in the doc vectors for this SUBCLASS
        w2v = KeyedVectors.load_word2vec_format("{}/{}/{}_w2v_{}_docs.bin".format(DIR, VEC_PATH, cpc, 'SG'), binary=True)
        count = 0
        # go through the top results for this SUBCLASS
        for a, b in w2v.similar_by_vector(v, topn=len(w2v.wv.vocab)):
            if count >= MAX_PRIOR_ART: break # stop when we have enough results
            if priority_date > -1: # if the user specified a priority date
                d = int(dates[cpc][a]) # get the date of this prior art
                if d <= priority_date: # check if the date is before/on the priority date
                    results_pa[a] = b # record prior art score
                    results_cpc[a] = cpc # record prior art subclass
                    count +=1
            else:
                results_pa[a] = b # record prior art score
                results_cpc[a] = cpc # record prior art subclass
                count +=1
    pa = [(p_n, results_cpc[p_n]) for p_n in sorted(results_pa, key=results_pa.get, reverse=True)]
    save_prior_art(pa, c_id, email, project_name)
    return pa

def step_2_get_prior_art(cpc_subclasses, c_id, email, project_name, priority_date):
    results_pa, results_cpc, v = {}, {}, np.loadtxt('{}/clients/{}/{}/{}/input_vector_{}.txt'.format(DIR, c_id, email, project_name, cpc_subclasses[0][0]), dtype=np.float32)
    dates = {} # this is for filtering by priority date
    # go through each chosen subclass
    for cpc in cpc_subclasses:
        if priority_date > -1: dates[cpc] = get_dates('{}/{}/{}.txt'.format(DIR, DATE_PATH, cpc))
        # read in the doc vectors for this SUBCLASS
        w2v = KeyedVectors.load_word2vec_format("{}/{}/{}_w2v_{}_docs.bin".format(DIR, VEC_PATH, cpc, 'SG'), binary=True)
        # go through the top results for this SUBCLASS
        for a, b in w2v.similar_by_vector(v, topn=MAX_PA_CUTOFF):
            # if the user specified a priority date
            if priority_date > -1 and int(dates[cpc][a]) > priority_date: continue
            results_pa[a] = b # record prior art score
            results_cpc[a] = cpc # record prior art subclass
    pa = cull_prior_art(results_pa, results_cpc)
    save_prior_art(pa, c_id, email, project_name)
    return pa

def cull_prior_art(results_pa, results_cpc):
    # get the top 500 results across all CPC subclasses
    s = sorted(results_pa, key=results_pa.get, reverse=True)[:MAX_PA_CUTOFF]
    # check if there's already a manageable number of results
    if len(s) < MAX_PA_CUTOFF-100: # e.g. 400
        return [(p_n, results_cpc[p_n]) for p_n in s]
    # cull the results further, by percentage similarity
    x, y = results_pa[s[0]] - 0.05, results_pa[s[0]] - 0.1 # 5% or 10% difference from the top result
    for i in range(len(s)):
        # less than 60% but at least 25 results; or less than 5% but at least 350 results; or less than 10% but at least 250 results
        if (results_pa[s[i]] < 0.6 and i >= 25) or (results_pa[s[i]] < x and i >= 350) or (results_pa[s[i]] < y and i >= 250):
            return [(p_n, results_cpc[p_n]) for p_n in s[:i]]
    # normally wouldn't get to this point, only if all 400+ results are within 5% from top result
    return [(p_n, results_cpc[p_n]) for p_n in s]

# COMPLETE THIS LATER!
def get_top_applicants(prior_art, c_id, email, project_name):
    # GO THROUGH PRIOR ART AND GET A LIST OF e.g. 15-20 TOP applicants
    top_applicants = ['Google', 'IBM', 'Microsoft', 'Facebook', 'Monsanto'] # PLACEHOLDER!
    with codecs.open('{}/clients/{}/{}/{}/applicants.txt'.format(DIR, c_id, email, project_name), 'w', 'utf-8') as f_out:
        f_out.write(u'\n'.join(top_applicants))

def get_result_elements(prior_art, c_id, email, project_name, updated=False):
    result_elements, essential_elements, CPC_subclasses = {}, None, set([y for _, y in prior_art])
    # go through each CPC subclass
    for cs in CPC_subclasses:
        # retrieve essential elements mapping for this CPC subclass
        essential_elements = get_mapping_essential_elements('{}/{}/{}.txt'.format(DIR, ELEM_PATH, cs), [x for x, y in prior_art if y == cs])
        # go through each prior art result
        for p, c in prior_art:
            if c != cs: continue # skip if this isn't the right CPC subclass
            if p not in essential_elements: continue # CAN HAPPEN FOR SOME REASON! skip if patent # isn't in essential elements
            # go through each essential element for this prior art result
            for e in essential_elements[p]:
                # keep track of this essential element's frequency
                result_elements[e] = result_elements[e]+1 if e in result_elements else 1
    # go through the top result elements
    top_result_elements = []
    p90 = np.percentile(result_elements.values(), 90) # calculate 90th percentile
    for r in sorted(result_elements, key=result_elements.get, reverse=True):
        if result_elements[r] < p90 or len(top_result_elements) >= MAX_RESULT_ELEMENTS: break # keep it at max number of elements!
        # check if this result element is different enough from input elements & from previous result elements
        x = set(r.split()) # make a set out of the result element
        too_similar = False
        for e in top_result_elements:
            if r in e or e in r:
                too_similar = True
                break
            y = set(e.split()) # make a set out of each element already added
            # handle tricky case where elems are similar enough but not subsumed by each other
            # i.e. fraction of words is the same: 2/3, 3/4, and 3/5
            if len(x.intersection(y)) / float(max(len(x), len(y))) >= 0.6:
                too_similar = True
                break
            # if it's a 2-word result element, try to reverse the words
            z = None
            if len(r.split()) == 2:
                z = u'{} {}'.format(r.split()[1], r.split()[0])
            # check the Levenshtein distance
            max_dist = 4 if len(r) >= 10 else 3
            if Levenshtein.distance(u'{}'.format(r), u'{}'.format(e)) <= max_dist or (z != None and Levenshtein.distance(u'{}'.format(z), u'{}'.format(e)) <= max_dist):
                too_similar = True
                break
        if not too_similar: top_result_elements.append(r)
    # last step - save the result elements
    f_name = 'updated_result_elements' if updated else 'result_elements'
    with codecs.open('{}/clients/{}/{}/{}/{}.txt'.format(DIR, c_id, email, project_name, f_name), 'w', 'utf-8') as f_out:
        f_out.write(u'\n'.join(top_result_elements))

def get_filters(c_id, email, project_name):
    filters = []
    # (1) get the key elements
    filters.append({'key_elements': []})
    # (2) get the result elements
    try:
        re = get_list('{}/clients/{}/{}/{}/updated_result_elements.txt'.format(DIR, c_id, email, project_name))
    except:
        re = get_list('{}/clients/{}/{}/{}/result_elements.txt'.format(DIR, c_id, email, project_name))
    filters.append({'result_elements': re})
    # (3) get the chosen CPC subclasses
    filters.append({'cpc_subclasses': get_list('{}/clients/{}/{}/{}/chosen_subclasses.txt'.format(DIR, c_id, email, project_name))})
    return filters

def get_filtersX(c_id, email, project_name):
    filters = []
    # (1) get the key elements
    filters.append({'key_elements': []})
    # (2) get the result elements
    filters.append({'result_elements': get_list('{}/clients/{}/{}/{}/result_elements.txt'.format(DIR, c_id, email, project_name))})
    # (3) get the chosen CPC subclasses
    filters.append({'cpc_subclasses': get_list('{}/clients/{}/{}/{}/chosen_subclasses.txt'.format(DIR, c_id, email, project_name))})
    # (4) get the chosen CPC subclasses
    filters.append({'applicants': get_list('{}/clients/{}/{}/{}/applicants.txt'.format(DIR, c_id, email, project_name))})
    return filters

def check_key_elements(key_elements):
    # key_elements = list of Strings entered by the user
    ok_elems, already_seen, count = [], set(), 0
    for e in key_elements: # go through each key element
        count +=1
        # make sure no duplicates
        if e in already_seen:
            return True, {'ELEMENT_ERROR': 'This element is a duplicate. Please enter original elements.', 'ELEMENT_NUMBER': count}
        # make sure length is fine
        if len(e.split()) > 5:
            return True, {'ELEMENT_ERROR': 'This element is too long. Please keep it to 5 words or less.', 'ELEMENT_NUMBER': count}
        already_seen.add(e)
        ok_elems.append(e)
        
    return False, ok_elems

def filter_results(formatted_results, filters, c_id, email, project_name, w2v=None):
    # formatted_results = list of dict objects {'p': patent number, 't': title, 'c': CPC subclass, 's': 0/1}
    # filters = dict with filters, e.g. {'key_elements': ['air filter', 'handheld'], 'date_from': 20150101}
    # check if the user wants to match any key_elements
    if 'key_elements' in filters:
        # get the section first
        if 'cpc_subclasses' in filters:
            section = filters['cpc_subclasses'][0][0]
        else: # read in the stored section
            with codecs.open('{}/clients/{}/{}/{}/cpc_section.txt'.format(DIR, c_id, email, project_name), 'r', 'utf-8') as f:
                section = f.read().strip() # e.g. 'A'
        # load the word vectors for this section
        if w2v == None: # probably don't need this, but just in case
            w2v = KeyedVectors.load("{}/{}/{}_w2v_{}_words-normed".format(DIR, VEC_PATH, section, 'SG'), mmap='r')
            w2v.vectors_norm = w2v.vectors
        # load the OOV word vectors for this section
        w2v_oov = KeyedVectors.load_word2vec_format("{}/{}/{}_OOV.bin".format(DIR, ELEM_PATH, section), binary=True)
        # load the input elements - technically shouldn't need this, but see the lines below
        input_elements = get_list('{}/clients/{}/{}/{}/input_elements.txt'.format(DIR, c_id, email, project_name))
        # load the input vectors
        input_vectors = np.loadtxt('{}/clients/{}/{}/{}/input_elements_vectors.txt'.format(DIR, c_id, email, project_name), dtype=np.float32) # list
        if len(input_elements) == 1: input_vectors = [input_vectors] # it there's only 1 vector, make a list out of it
        input_vectors = dict(zip(input_elements, input_vectors)) # make it into a dict w/ keys = elements & values = vectors
        min_score = 0.75 # could be as high as 0.9
    # go through each formatted result and build a new list
    filtered_results, dates, essential_elements = [], {}, {}
    # if we're not narrowing by CPC subclasses, look at only the top results
    if 'cpc_subclasses' not in filters:
        formatted_results = formatted_results[:MAX_PRIOR_ART]
    # check if there are any filters other than CPC subclass
    no_filters = not ('date_from' in filters or 'date_to' in filters or 'key_elements' in filters or 'result_elements' in filters)
    for r in formatted_results:
        temp_result = {} # for building a new result entry
        cpc_match = False # for checking if it's a match based on CPC subclass
        # (1) check for any specified CPC subclasses
        if 'cpc_subclasses' in filters:
            if r['c'] not in filters['cpc_subclasses']:
                continue
            else:
                cpc_match = True
        # (2) check for any specified dates
        if 'date_from' in filters or 'date_to' in filters:
            if r['c'] not in dates: dates[r['c']] = get_dates('{}/{}/{}.txt'.format(DIR, DATE_PATH, r['c']))
            d = int(dates[r['c']][r['p'][2:]])
            if 'date_from' in filters and d < filters['date_from']: continue
            if 'date_to' in filters and d > filters['date_to']: continue
            temp_result['d'] = '{}-{}-{}'.format(str(d)[:4], str(d)[4:6], str(d)[6:])
        # next, check for key or result elements
        if 'key_elements' in filters or 'result_elements' in filters:
            if r['c'] not in essential_elements: essential_elements[r['c']] = get_mapping('{}/{}/{}.txt'.format(DIR, ELEM_PATH, r['c']))
            if r['p'][2:] not in essential_elements[r['c']]: continue # CAN HAPPEN FOR SOME REASON! skip if patent # isn't in essential elements
            # (3) check for any specified result elements
            if 'result_elements' in filters:
                temp_result_elements = []
                # go through each result element filter
                for r_e in filters['result_elements']:
                    if r_e in essential_elements[r['c']][r['p'][2:]]:
                        temp_result_elements.append(r_e)
                if temp_result_elements:
                    temp_result['r'] = temp_result_elements
            # (4) check for any specified key elements
            if 'key_elements' in filters:
                temp_key_elements, already_recorded = [], []
                # get the vectors for each essential element for this pa result
                ee_vectors = {e: get_vector(e, w2v, w2v_oov) for e in essential_elements[r['c']][r['p'][2:]]}
                # go through each key/input element filter
                for k_e in filters['key_elements']:
                    m = None # match
                    # go through each essential element for this pa result
                    for e_e in essential_elements[r['c']][r['p'][2:]]:
                        if not any(ee_vectors[e_e]): continue # VERY RARE case
                        ss = cos(input_vectors[k_e], ee_vectors[e_e]) # get a similarity score
                        # check if score exceeds threshold & other things
                        if ss > min_score and e_e not in already_recorded and len(e_e.split()) >= len(k_e.split()):
                            m = e_e
                            break
                    if m:
                        already_recorded.append(m)
                        if k_e == m:
                            temp_key_elements.append(m)
                        else:
                            temp_key_elements.append('{} ("{}")'.format(k_e, m))
                if temp_key_elements:
                    temp_result['k'] = temp_key_elements
        # check if no filters were added
        if not temp_result and not (cpc_match and no_filters): continue
        # add the original info
        temp_result['p'] = r['p']
        temp_result['c'] = r['c']
        temp_result['t'] = r['t']
        temp_result['s'] = r['s']
        # add the new result entry to the list
        filtered_results.append(temp_result)
    return filtered_results[:MAX_PRIOR_ART]

def filter_resultsX(formatted_results, filters, c_id, email, project_name, updated=False):
    # formatted_results = list of dict objects {'p': patent number, 't': title, 'c': CPC subclass, 's': 0/1}
    # filters = dict with filters, e.g. {'key_elements': ['air filter', 'handheld'], 'date_from': 20150101}
    # go through each formatted result and build a new list
    filtered_results, dates, essential_elements = [], {}, {}
    # check if there are any filters other than CPC subclass
    no_filters = not ('date_from' in filters or 'date_to' in filters or 'key_elements' in filters or 'result_elements' in filters or 'applicants' in filters)
    for r in formatted_results:
        temp_result = {} # for building a new result entry
        cpc_match = False # for checking if it's a match based on CPC subclass
        # (1) check for any specified CPC subclasses
        if 'cpc_subclasses' in filters:
            if r['c'] not in filters['cpc_subclasses']:
                continue
            else:
                cpc_match = True
        # (2) check for any specified dates
        if 'date_from' in filters or 'date_to' in filters:
            if r['c'] not in dates: dates[r['c']] = get_dates('{}/{}/{}.txt'.format(DIR, DATE_PATH, r['c']))
            d = int(dates[r['c']][r['p'][2:]])
            if 'date_from' in filters and d < filters['date_from']: continue
            if 'date_to' in filters and d > filters['date_to']: continue
            temp_result['d'] = '{}-{}-{}'.format(str(d)[:4], str(d)[4:6], str(d)[6:])
        # (3) check for any specified applicants
        if 'applicants' in filters:
            # get the Applicant for this result - FILL IN LATER!
            temp_applicant = 'IBM' # PLACEHOLDER
            if temp_applicant in filters['applicants']:
                temp_result['a'] = temp_applicant
        # next, check for key or result elements
        if 'key_elements' in filters or 'result_elements' in filters:
            if r['c'] not in essential_elements: essential_elements[r['c']] = get_mapping('{}/{}/{}.txt'.format(DIR, ELEM_PATH, r['c']))
            if r['p'][2:] not in essential_elements[r['c']]: continue # CAN HAPPEN FOR SOME REASON! skip if patent # isn't in essential elements
            # (3) check for any specified result elements
            if 'result_elements' in filters:
                temp_result_elements = []
                # go through each result element filter
                for r_e in filters['result_elements']:
                    if r_e in essential_elements[r['c']][r['p'][2:]]:
                        temp_result_elements.append(r_e)
                if temp_result_elements:
                    temp_result['r'] = temp_result_elements
            # (4) check for any specified key elements
            if 'key_elements' in filters:
                temp_key_elements = []
                # go through each key element filter
                for k_e in filters['key_elements']:
                    if k_e in essential_elements[r['c']][r['p'][2:]]:
                        temp_key_elements.append(k_e)
                if temp_key_elements:
                    temp_result['k'] = temp_key_elements
        # check if no filters were added
        if not temp_result and not (cpc_match and no_filters): continue
        # add the original info
        temp_result['p'] = r['p']
        temp_result['c'] = r['c']
        temp_result['t'] = r['t']
        temp_result['s'] = r['s']
        if updated: temp_result['x'] = r['x']
        # add the new result entry to the list
        filtered_results.append(temp_result)
    return filtered_results

def add_filters_to_results(formatted_results, c_id, email, project_name):
    # formatted_results = list of dict objects {'p': patent number, 't': title, 'c': CPC subclass, 's': 0/1}
    # get the previously applied filters; dict: {pat_num: String separated by '@'}
    filters = {l.strip().split(':')[0]: l.strip().split(':')[1] for l in codecs.open('{}/clients/{}/{}/{}/filtered_results_filters.txt'.format(DIR, c_id, email, project_name), 'r', 'utf-8')}
    filtered_results = []
    for r in formatted_results:
        temp = r # build a new result entry, starting by incorporating the old
        options = filters[temp['p']].split('@')
        if options[0] != '_': temp['k'] = options[0].split(',')
        if options[1] != '_': temp['r'] = options[1].split(',')
        if options[2] != '_': temp['d'] = options[2]
        filtered_results.append(temp)
    return filtered_results

def add_filters_to_resultsX(formatted_results, c_id, email, project_name):
    # formatted_results = list of dict objects {'p': patent number, 't': title, 'c': CPC subclass, 's': 0/1}
    # get the previously applied filters; dict: {pat_num: String separated by '@'}
    filters = {l.strip().split(':')[0]: l.strip().split(':')[1] for l in codecs.open('{}/clients/{}/{}/{}/filtered_results_filters.txt'.format(DIR, c_id, email, project_name), 'r', 'utf-8')}
    filtered_results = []
    for r in formatted_results:
        temp = r # build a new result entry, starting by incorporating the old
        options = filters[temp['p']].split('@')
        if options[0] != '_': temp['k'] = options[0].split(',')
        if options[1] != '_': temp['r'] = options[1].split(',')
        if options[2] != '_': temp['d'] = options[2]
        if options[3] != '_': temp['a'] = options[3]
        filtered_results.append(temp)
    return filtered_results

def compare_results(new_results_pa, new_results_cpc, prev_results):
    count, prev_pa, compared_results = 0, [x[0] for x in prev_results], []
    for p in [p_n for p_n in sorted(new_results_pa, key=new_results_pa.get, reverse=True)]:
        compared_results.append((p, new_results_cpc[p], prev_pa.index(p)-count))
        count +=1 
    p10 = np.percentile([x[2] for x in compared_results], 10) # calculate 10th percentile
    return [x for x in compared_results if x[2] >= p10] # discard any results below 10th percentile

def get_updated_results(input_saved_pa, cpc_subclasses, vectors_exist, results_exist, c_id, email, project_name, priority_date):
    # get the previous input vectors
    if vectors_exist:
        prev_vecs = np.loadtxt('{}/clients/{}/{}/{}/updated_results_vectors.txt'.format(DIR, c_id, email, project_name), dtype=np.float32) # list
        v_avg = prev_vecs[0]
        v_sub = prev_vecs[1]
        v_add = prev_vecs[2]
    else:
        v_avg = np.loadtxt('{}/clients/{}/{}/{}/input_vector.txt'.format(DIR, c_id, email, project_name), dtype=np.float32)
        v_sub = np.loadtxt('{}/clients/{}/{}/{}/input_vector.txt'.format(DIR, c_id, email, project_name), dtype=np.float32)
        v_add = np.loadtxt('{}/clients/{}/{}/{}/input_vector.txt'.format(DIR, c_id, email, project_name), dtype=np.float32)
    # go through the input prior art & modify the vectors
    w2v_docs = {}
    for p, c in input_saved_pa:
        if c not in w2v_docs: w2v_docs[c] = KeyedVectors.load_word2vec_format("{}/{}/{}_w2v_{}_docs.bin".format(DIR, VEC_PATH, c, 'SG'), binary=True)
        v_avg = (v_avg + w2v_docs[c][p]) / 2.0 # average the two vectors
        v_sub = v_sub - w2v_docs[c][p] # subtract the two vectors
        v_add = v_add + w2v_docs[c][p] # add the two vectors
    # save the modified vectors
    with codecs.open('{}/clients/{}/{}/{}/updated_results_vectors.txt'.format(DIR, c_id, email, project_name), 'w', 'utf-8') as f_v:
        for v in [v_avg, v_sub, v_add]:
            np.savetxt(f_v, v, newline=' ', comments='')
            f_v.write('\n')
    # get the previous prior art results
    if results_exist:
        prev_results = read_prior_art('{}/clients/{}/{}/{}/updated_results_previous.txt'.format(DIR, c_id, email, project_name))
    else: # if this is the first iteration
        # grab the original results
        prev_results = read_prior_art('{}/clients/{}/{}/{}/prior_art_results.txt'.format(DIR, c_id, email, project_name))
        # store the original results
        with codecs.open('{}/clients/{}/{}/{}/updated_results_previous.txt'.format(DIR, c_id, email, project_name), 'w', 'utf-8') as f:
            f.write('\n'.join(['{}:{}'.format(x, y) for x, y in prev_results[:MAX_PRIOR_ART]])+'\n')
    # go through each cpc subclass & get prior art
    prev_results_set, new_results_pa, new_results_cpc = set(zip(*prev_results)[0]), {}, {}
    dates = {} # this is for filtering by priority date
    for cpc in cpc_subclasses:
        if priority_date > -1: dates[cpc] = get_dates('{}/{}/{}.txt'.format(DIR, DATE_PATH, cpc))
        if cpc not in w2v_docs: w2v_docs[cpc] = KeyedVectors.load_word2vec_format("{}/{}/{}_w2v_{}_docs.bin".format(DIR, VEC_PATH, cpc, 'SG'), binary=True)
        # do this for all three vectors
        for v in [v_avg]: # [v_avg, v_sub, v_add]
            count = 0
            for a, b in w2v_docs[cpc].similar_by_vector(v, topn=len(w2v_docs[cpc].wv.vocab)):
                if count >= MAX_PRIOR_ART: break
                if a not in prev_results_set and a not in new_results_pa:
                    if priority_date > -1:
                        d = int(dates[cpc][a]) # get the date of this prior art
                        if d <= priority_date: # check if the date is before/on the priority date
                            new_results_pa[a] = b # record prior art score
                            new_results_cpc[a] = cpc # record prior art subclass
                            count +=1
                    else:
                        new_results_pa[a] = b # record prior art score
                        new_results_cpc[a] = cpc # record prior art subclass
                        count +=1
    # clear the variable, just in case
    w2v_docs = None
    pa = [(p_n, new_results_cpc[p_n]) for p_n in sorted(new_results_pa, key=new_results_pa.get, reverse=True)]
    return pa

def step_3_get_updated_results(input_saved_pa, cpc_subclasses, c_id, email, project_name):
    # get the section first
    section = cpc_subclasses[0][0]
    # try to get the previous input vectors, if any
    try:
        prev_vecs = np.loadtxt('{}/clients/{}/{}/{}/updated_results_vectors.txt'.format(DIR, c_id, email, project_name), dtype=np.float32) # list
        v_avg = prev_vecs[0]
        v_sub = prev_vecs[1]
        v_add = prev_vecs[2]
    except:
        v_avg = np.loadtxt('{}/clients/{}/{}/{}/input_vector_{}.txt'.format(DIR, c_id, email, project_name, section), dtype=np.float32)
        v_sub = np.loadtxt('{}/clients/{}/{}/{}/input_vector_{}.txt'.format(DIR, c_id, email, project_name, section), dtype=np.float32)
        v_add = np.loadtxt('{}/clients/{}/{}/{}/input_vector_{}.txt'.format(DIR, c_id, email, project_name, section), dtype=np.float32)
    # go through the input prior art & modify the vectors
    w2v_docs = {}
    for p, c in input_saved_pa:
        if c not in w2v_docs: w2v_docs[c] = KeyedVectors.load_word2vec_format("{}/{}/{}_w2v_{}_docs.bin".format(DIR, VEC_PATH, c, 'SG'), binary=True)
        v_avg = (v_avg + w2v_docs[c][p]) / 2.0 # average the two vectors
        v_sub = v_sub - w2v_docs[c][p] # subtract the two vectors
        v_add = v_add + w2v_docs[c][p] # add the two vectors
    # save the modified vectors
    with codecs.open('{}/clients/{}/{}/{}/updated_results_vectors.txt'.format(DIR, c_id, email, project_name), 'w', 'utf-8') as f_v:
        for v in [v_avg, v_sub, v_add]:
            np.savetxt(f_v, v, newline=' ', comments='')
            f_v.write('\n')
    # try to get the previous prior art results, if any
    try:
        prev_results = read_prior_art('{}/clients/{}/{}/{}/updated_results_current.txt'.format(DIR, c_id, email, project_name))
    except: # if this is the first iteration
        # grab the original results
        prev_results = read_prior_art('{}/clients/{}/{}/{}/prior_art_results.txt'.format(DIR, c_id, email, project_name))
    # go through the existing prior art & re-calculate similarity scores
    new_results_pa, new_results_cpc = {}, {}
    for p, c in prev_results:
        if c not in w2v_docs: w2v_docs[c] = KeyedVectors.load_word2vec_format("{}/{}/{}_w2v_{}_docs.bin".format(DIR, VEC_PATH, c, 'SG'), binary=True)
        new_results_pa[p] = cos(v_avg, w2v_docs[c][p])
        new_results_cpc[p] = c
    # compare the new results to the previous results
    compared_results = compare_results(new_results_pa, new_results_cpc, prev_results)
    # save the compared results
    with codecs.open('{}/clients/{}/{}/{}/updated_results_current.txt'.format(DIR, c_id, email, project_name), 'w', 'utf-8') as f:
        f.write('\n'.join(['{}:{}:{}'.format(x, y, z) for x, y, z in compared_results])+'\n')
    return compared_results

def get_abstract(p_n, cpc):
    abstracts = get_abstracts('{}/{}/{}.txt'.format(DIR, ABSTRACT_PATH, cpc))
    return abstracts[p_n] if p_n in abstracts else "NO ABSTRACT AVAILABLE."

