import sys
import re
import string
import json
import time
import types
import sqlite3
from text.classifiers import NaiveBayesClassifier
from text.classifiers import DecisionTreeClassifier

import logging
global LOG_CONFIG
LOG_CONFIG = { 'level': logging.DEBUG }
try:
    import log
except ImportError:
    pass

# Identity feature extractor
def token_extractor(document):
    return dict((token,True) for token in document.split())

punct_re = re.compile(r'[' + string.punctuation + ']')
def get_description_tokens(items):
    desc = ' '.join(items.get('http://dbpedia.org/property/shortDescription', []) +
                    items.get('http://purl.org/dc/elements/1.1/description', []) +
                    items.get('http://purl.org/dc/elements/1.1/description', []))
    tokens = set(punct_re.sub(' ', desc.lower()).split())
    return tokens

def pairs_to_dict(pairs):
    d = {}
    for p,o in pairs:
        if p not in d:
            d[p] = []
        d[p].append(o)
    d['description_tokens'] = get_description_tokens(d)
    return d

def predict_politician(items):
    keys = ["http://dbpedia.org/ontology/successor",
            "http://dbpedia.org/ontology/predecessor",
            "http://dbpedia.org/ontology/orderInOffice"]
    for key in keys:
        if key in items:
            return True

    tokens = items['description_tokens']
    keywords = set(['politician', 'judge', 'mayor', 'congressman', 'senator',
                    'elected', 'governor', 'representative', 'congresswoman',
                    'secretary', 'candidate', 'prime', 'lady', 'president'])
    return len(tokens & keywords) > 0

def predict_policy(items):
    tokens = items['description_tokens']
    keywords = set(['policy', 'lobby', 'lobbyist', 'ngo', 'planned', 'parenthood', 'advocate', 'advocacy', 'organization', 'consultant', 'activist'])
    return len(tokens & keywords) > 0

def predict_academic(items):
    keys = ["http://dbpedia.org/property/workInstitutions"]
    for key in keys:
        if key in items:
            return True

    tokens = items['description_tokens']
    keywords = set(['professor', 'academic', 'phd', 'hd', 'dr', 'scientist', 'university', 'institute', 'historian'])
    return len(tokens & keywords) > 0

def predict_journalist(items):
    pairs = [("http://dbpedia.org/ontology/occupation", "http://dbpedia.org/resource/Journalist"),
             ("http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "http://dbpedia.org/class/yago/Reporter110521662")]
    for key, value in pairs:
        if value in items.get(key, []):
            return True

    tokens = items['description_tokens']
    keywords = set(['journalist', 'news', 'newsmedia', 'correspondent', 'commentator', 'host', 'moderator',
                    'cnn', 'fox', 'nbc', 'abc', 'cbs', 'msnbc', 'post', 'times', 'tribune', 'magazine', 'newspaper'])
    return len(tokens & keywords) > 0

def predict_musician(items):
    pairs = []
    for key, value in pairs:
        if value in items.get(key, []):
            return True

    tokens = items['description_tokens']
    keywords = set(['musician', 'singer', 'song', 'songwriter', 'band', 'performer', 'guitar', 'piano'])
    return len(tokens & keywords) > 0

def predict_comedian(items):
    pairs = [("http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "http://dbpedia.org/class/yago/Comedian109940146")]
    for key, value in pairs:
        if value in items.get(key, []):
            return True

    tokens = items['description_tokens']
    keywords = set(['comedian', 'comic'])
    return len(tokens & keywords) > 0

def predict_actor(items):
    pairs = [("http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "http://dbpedia.org/class/yago/DocumentaryFilmDirectors"),
             ("http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "http://dbpedia.org/class/yago/AmericanFilmDirectors")]
    for key, value in pairs:
        if value in items.get(key, []):
            return True

    tokens = items['description_tokens']
    keywords = set(['actor', 'actress', 'director', 'filmaker', 'filmmaker', 'screenwriter', 'artist', 'entertainer', 'entertainment'])
    return len(tokens & keywords) > 0

def predict_athlete(items):
    tokens = items['description_tokens']
    keywords = set(['athlete', 'sports', 'football', 'soccer', 'baseball', 'basketball', 'tennis', 'hockey', 'olympic', 'olympics'])
    return len(tokens & keywords) > 0

def predict_writer(items):
    tokens = items['description_tokens']
    keywords = set(['writer', 'poet', 'author', 'novel', 'novelist'])
    return len(tokens & keywords) > 0

def predict_clergy(items):
    tokens = items['description_tokens']
    keywords = set(['clergyman', 'reverend', 'bishop', 'pope', 'pastor', 'rabbi'])
    return len(tokens & keywords) > 0

def predict_business(items):
    tokens = items['description_tokens']
    keywords = set(['business', 'businessman', 'ceo', 'ipo', 'stock'])
    return len(tokens & keywords) > 0


def get_class_label(p):
    return p.replace('predict_', '').title()

module = sys.modules[__name__]
predictors = [module.__dict__.get(a) for a in dir(module) if isinstance(module.__dict__.get(a), types.FunctionType) and a.startswith("predict_")]

def train_classifiers(labeled_data, N):
    # Create a classifier for each class
    classifiers = {}
    for predictor in predictors:
        label = get_class_label(predictor.__name__)
        classifiers[label] = NaiveBayesClassifier([], token_extractor)

    # For each labeled example, train all classifiers as either positive or negative example
    for features,label in labeled_data[:N]:
        for c in classifiers:
            if label == c:
                classifiers[c].update([(features,"positive")])
            else:
                classifiers[c].update([(features,"negative")])


if __name__=="__main__":
    db_file = sys.argv[1]
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT eid, resource, dbpedia FROM episodes " +
                   "JOIN appearances USING (eid) " +
                   "JOIN guests USING (resource) " +
                   "ORDER BY airdate")

    rows = cursor.fetchall()
    for row in rows:
        log.info("episode %s, resource %s", row['eid'], row['resource'])

        predicate_objects = json.loads(row['dbpedia'])
        properties = pairs_to_dict(predicate_objects)

        label = 'Unknown'
        for predictor in predictors:
            if predictor(properties):
                label = get_class_label(predictor.__name__)
                log.info('\t%s', label)

                # TBD: Write label to database

    #raw_input("Press Enter to train classifiers using the pseudo-labeled data...")

    # TBD: Find labeled data in database

    #classifiers = train_classifiers(labeled_data, 200)

    # TBD: Find unlabeled data in database, classify it

    #results = [(unlabeled_resources[i],
    #            dict((c,classifiers[c].prob_classify(unlabeled_data[i][0]).prob('positive'))
    #                 for c in classifiers))
    #           for i in range(len(unlabeled_data))]

    # TBD: Write SSL labels to database with confidences

    #for resource, predictions in results:
    #    print "%s" % resource
    #    sorted_predictions = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
    #    for i in range(3):
    #        print "\t%0.3f\t%s" % (sorted_predictions[i][1], sorted_predictions[i][0])
    #    print ""
