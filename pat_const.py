PREP = ['with', 'at', 'from', 'into', 'during', 'including', 'include', 'includes', 'until',
             'against', 'among', 'throughout', 'despite', 'toward', 'towards', 'upon', 'concerning', 'of', 'to', 'in', 'for',
             'on', 'by', 'about', 'like', 'through', 'over', 'before', 'between', 'after', 'since', 'without', 'under',
             'within', 'along', 'following', 'across', 'behind', 'beyond', 'plus', 'except', 'but', 'up', 'out',
             'around', 'down', 'off', 'above', 'near', 'onto', 'away']

DET = ['a', 'an', 'the', 'this', 'that', 'these', 'those', 'my', 'your', 'his', 'her', 'its', 'our', 'their',
               'few', 'little', 'much', 'many', 'lot', 'most', 'some', 'any', 'enough', 'one', 'two', 'three', 'four',
               'five', 'six', 'seven', 'eight', 'nine', 'ten', 'all', 'both', 'either', 'neither', 'each', 'every',
               'other', 'another', 'such', 'what', 'rather', 'quite']

CONJ = ['and', 'or', 'nor', 'yet', 'so', 'although', 'as', 'if', 'long', 'soon', 'though', 'because', 'than', 'unless',
        'when', 'whenever', 'where', 'wherever', 'while', 'whether', 'only', 'also', 'via']

PRN = ['i', 'me', 'we', 'us', 'you', 'she', 'her', 'him', 'it', 'they', 'them', 'whom']

ADV = ['substantially', 'partly', 'very', 'entire', 'entirely', 'directly', 'indirectly', 'quickly', 'fast', 'slow',
       'partially', 'uniquely', 'easily', 'simply', 'additionally', 'naturally', 'preferably', 'generally', 'consequently',
       'particularly', 'ultimately', 'especially', 'evenly', 'unevenly', 'respectively', 'greater', 'primary',
       'secondary', 'tertiary', 'approximately', 'relative', 'selectively', 'together', 'apart', 'intermediate', 'wide',
       'narrow', 'close', 'closest', 'far', 'farthest', 'furthest', 'specifically', 'independent', 'independently',
       'subsequently']

STOP = ['least', 'providing', 'provided', 'wherein', 'further', 'method', 'apparatus', 'device', 'system', 'comprise',
        'comprises', 'comprising', 'just', 'being', 'had', 'has', 'should', 'do', 'doing', 'did', 'not', 'now', 'is',
        'are', 'does', 'be', 'were', 'here', 'been', 'too', 'was', 'more', 'less', 'will', 'below', 'can', 'then', 'itself',
        'have', 'having', 'again', 'no', 'same', 'how', 'which', 'why', 'once', 'twice', 'thereof', 'therefor', 'said', 'relate',
        'relates', 'plurality', 'according', 'accordance', 'certain', 'particular', 'specific', 'constitute', 'constitutes', 'constituting', 'use',
        'using', 'take', 'taken', 'characterize', 'characterized', 'characterizes', 'improve', 'improved', 'improving',
        'improves', 'therefore', 'named', 'making', 'make', 'made', 'claim', 'claims', 'claimed', 'claiming', 'thereon', 'supporting',
        'support', 'methods', 'iii', 'systems', 'devices', 'containing', 'producing', 'multiple', 'embodiment', 'embodiments',
        'disclose', 'disclosed', 'herein', 'important', 'importance', 'useful', 'advantage', 'advantageous', 'improvement',
        'various', 'different', 'function', 'accomplish', 'accomplished', 'invention', 'typical', 'additional', 'upper', 'lower',
        'left', 'right', 'reference', 'refer', 'referring', 'referred', 'fig', 'figure', 'drawing', 'drawings', 'form', 'forming',
        'formed', 'similar', 'inside', 'item', 'desire', 'desired', 'set', 'associated', 'coupled', 'first', 'second',
        'top', 'bottom', 'outer', 'inner', 'high', 'higher', 'low' 'pair', 'element', 'elements', 'configured', 'part', 'unit', 'thereby', 'end', 'provide',
        'predetermined', 'present', 'provides', 'arranged', 'receiving', 'used', 'adjacent', 'means', 'may', 'main', 'portion', 'portions', 'well',
        'good', 'better', 'smaller', 'bigger', 'larger', 'faster', 'slower', 'etc', 'thus', 'therein', 'thereafter', 'third', 'fourth', 'forth',
        'fifth', 'sixth', 'seventh', 'eigth', 'ninth', 'tenth', 'closed', 'open', 'whereby', 'step', 'steps', 'otherwise', 'therebetween',
        'sample', 'example', 'examples', 'opposite', 'therethrough', 'respective', 'abstract', 'thereto', 'affix', 'affixed', 'number',
        'inch', 'inches', 'due', 'given', 'pair', 'degree', 'degrees', 'celsius', 'fahrenheit']

CONNECTORS = ['mounted', 'mounting', 'select', 'selects', 'selected', 'consists', 'consisting', 'operating', 'operable',
              'receive', 'receiving', 'opposing', 'opposed', 'controlling', 'aligned', 'securing', 'located', 'allow',
              'defining', 'positioned', 'engaging', 'detecting', 'determining', 'determined', 'positioning', 'extending',
              'connected', 'spaced', 'supported', 'based', 'securing', 'received', 'define', 'defining', 'defines', 'corresponding',
              'moving', 'extends', 'facing', 'connecting', 'inserted', 'disposed', 'adjusting', 'applying', 'applied',
              'attached', 'attaching', 'fixed', 'removing', 'removed', 'contacting', 'underlying', 'recited', 'indicating',
              'exceeding', 'paired', 'couple', 'couples', 'meet', 'meets', 'represent', 'represented', 'representing',
              'passing', 'performing', 'performed', 'satisfies', 'satisfied', 'satisfying', 'satisfy', 'describe',
              'described', 'describing']

ELEMENTS = set(PREP + DET + CONJ + PRN + ADV + STOP + CONNECTORS)

ALL = set(PREP + DET + CONJ + PRN + ADV + STOP)