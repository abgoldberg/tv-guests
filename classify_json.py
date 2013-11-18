import sys
import re
import string
import json
import time
import types
from text.classifiers import NaiveBayesClassifier
from text.classifiers import DecisionTreeClassifier

input_file = sys.argv[1]
#input_file = 'scrapy_tds/items.json.extended'
data = json.load(open(input_file))

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
    keywords = set(['politician', 'judge', 'mayor', 'congressman', 'senator'])
    return len(tokens & keywords) > 0

def predict_clergy(items):
    tokens = items['description_tokens']
    keywords = set(['clergyman', 'reverend', 'bishop', 'pope', 'pastor'])
    return len(tokens & keywords) > 0

def predict_business(items):
    tokens = items['description_tokens']
    keywords = set(['business', 'businessman'])
    return len(tokens & keywords) > 0

def predict_journalist(items):
    pairs = [("http://dbpedia.org/ontology/occupation", "http://dbpedia.org/resource/Journalist")]
    for key, value in pairs:
        if value in items.get(key, []):
            return True

    tokens = items['description_tokens']
    keywords = set(['journalist', 'news', 'newsmedia', 'correspondent', 'commentator'])
    return len(tokens & keywords) > 0

def predict_writer(items):
    tokens = items['description_tokens']
    keywords = set(['writer', 'poet', 'author', 'historian'])
    return len(tokens & keywords) > 0

def predict_academic(items):
    tokens = items['description_tokens']
    keywords = set(['professor', 'academic'])
    return len(tokens & keywords) > 0

def predict_athlete(items):
    tokens = items['description_tokens']
    keywords = set(['athlete', 'sports', 'football', 'soccer', 'baseball', 'basketball', 'tennis', 'hockey'])
    return len(tokens & keywords) > 0

def predict_actor(items):
    tokens = items['description_tokens']
    keywords = set(['actor', 'actress', 'director', 'filmaker', 'filmmaker', 'screenwriter', 'artist'])
    return len(tokens & keywords) > 0

def predict_comedian(items):
    pairs = [("http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "http://dbpedia.org/class/yago/Comedian109940146")]
    for key, value in pairs:
        if value in items.get(key, []):
            return True

    tokens = items['description_tokens']
    keywords = set(['comedian', 'comic'])
    return len(tokens & keywords) > 0

def predict_performer(items):
    pairs = []
    for key, value in pairs:
        if value in items.get(key, []):
            return True

    tokens = items['description_tokens']
    keywords = set(['musician', 'singer', 'song', 'songwriter', 'band', 'performer'])
    return len(tokens & keywords) > 0

def predict_activist(items):
    pairs = []
    for key, value in pairs:
        if value in items.get(key, []):
            return True

    tokens = items['description_tokens']
    keywords = set(['activist'])
    return len(tokens & keywords) > 0

def get_class_label(p):
    return p.replace('predict_', '').title()

module = sys.modules[__name__]
predictors = [module.__dict__.get(a) for a in dir(module) if isinstance(module.__dict__.get(a), types.FunctionType) and a.startswith("predict_")]

labeled_resources = []
labeled_data = []
unlabeled_resources = []
unlabeled_data = []
year_stats = {}

print "%50s" % ("Guest")
for idx,episode in enumerate(data):
    if len(episode['guest_predicate_objects']) > 0:
        print "%(date)s, %(year)s" % episode

    year = episode['year']
    if year not in year_stats:
        year_stats[year] = {}

    for resource,pairs in episode['guest_predicate_objects'].items():
        print "%50s" % (resource),

        properties = pairs_to_dict(pairs)

        label = 'Unknown'

        for predictor in predictors:
            if predictor(properties):
                unknown = False
                label = get_class_label(predictor.__name__)
                print '\t%s' % label

                if label not in year_stats[year]:
                    year_stats[year][label] = 0
                year_stats[year][label] += 1

                #labeled_data.append((' '.join(properties['description_tokens']), label))
                #labeled_data.append((' '.join(properties.keys()), label))
                #labeled_data.append((' '.join(properties.keys()) + ' ' + ' '.join([' '.join(v) for v in properties.values()]), label))
                labeled_data.append((' '.join(properties.keys() + list(properties['description_tokens'])), label))
                labeled_resources.append(resource)

        if label is 'Unknown':
            if label not in year_stats[year]:
                year_stats[year][label] = 0
            year_stats[year][label] += 1

            #unlabeled_data.append((' '.join(properties['description_tokens']), 'Unknown'))
            #unlabeled_data.append((' '.join(properties.keys()), 'Unknown'))
            #unlabeled_data.append((' '.join(properties.keys()) + ' ' + ' '.join([' '.join(v) for v in properties.values()]), 'Unknown'))
            unlabeled_data.append((' '.join(properties.keys() + list(properties['description_tokens'])), 'Unknown'))
            unlabeled_resources.append(resource)

        print ""

for year,counts in sorted(year_stats.items()):
    print "Year: %s" % year
    for label,count in sorted(counts.items()):
        print "\t%3d %s" % (count, label)

# Identity feature extractor
def token_extractor(document):
    return dict((token,True) for token in document.split())

# Create a classifier for each class
classifiers = {}
for predictor in predictors:
    label = get_class_label(predictor.__name__)
    classifiers[label] = NaiveBayesClassifier([], token_extractor)

# For each labeled example, train all classifiers as either positive or negative example
for features,label in labeled_data[:200]:
    for c in classifiers:
        if label == c:
            classifiers[c].update([(features,"positive")])
        else:
            classifiers[c].update([(features,"negative")])

results = [(unlabeled_resources[i],
            dict((c,classifiers[c].prob_classify(unlabeled_data[i][0]).prob('positive'))
                 for c in classifiers))
           for i in range(len(unlabeled_data))]

import pprint
pprint.pprint(results)

#classifier = NaiveBayesClassifier(labeled_data[:300])
#classifier = DecisionTreeClassifier(labeled_data[:150])

import pdb
pdb.set_trace()
