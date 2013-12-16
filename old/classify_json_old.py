import sys
import re
import string
import json
import time

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

def politician(items):
    keys = ["http://dbpedia.org/ontology/successor",
            "http://dbpedia.org/ontology/predecessor",
            "http://dbpedia.org/ontology/orderInOffice"]
    for key in keys:
        if key in items:
            return True

    tokens = items['description_tokens']
    keywords = set(['politician', 'judge', 'mayor', 'congressman', 'senator'])
    return len(tokens & keywords) > 0

def clergy(items):
    tokens = items['description_tokens']
    keywords = set(['clergyman', 'reverend', 'bishop', 'pope', 'pastor'])
    return len(tokens & keywords) > 0

def business(items):
    tokens = items['description_tokens']
    keywords = set(['business', 'businessman'])
    return len(tokens & keywords) > 0

def journalist(items):
    pairs = [("http://dbpedia.org/ontology/occupation", "http://dbpedia.org/resource/Journalist")]
    for key, value in pairs:
        if value in items.get(key, []):
            return True

    tokens = items['description_tokens']
    keywords = set(['journalist', 'news', 'newsmedia', 'correspondent', 'commentator'])
    return len(tokens & keywords) > 0

def writer(items):
    tokens = items['description_tokens']
    keywords = set(['writer', 'poet', 'author', 'historian'])
    return len(tokens & keywords) > 0

def academic(items):
    tokens = items['description_tokens']
    keywords = set(['professor', 'academic'])
    return len(tokens & keywords) > 0

def athlete(items):
    tokens = items['description_tokens']
    keywords = set(['athlete', 'sports', 'football', 'soccer', 'baseball', 'basketball', 'tennis', 'hockey'])
    return len(tokens & keywords) > 0

def actor(items):
    tokens = items['description_tokens']
    keywords = set(['actor', 'actress', 'director', 'filmaker', 'filmmaker', 'screenwriter', 'artist'])
    return len(tokens & keywords) > 0

def comedian(items):
    pairs = [("http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "http://dbpedia.org/class/yago/Comedian109940146")]
    for key, value in pairs:
        if value in items.get(key, []):
            return True

    tokens = items['description_tokens']
    keywords = set(['comedian', 'comic'])
    return len(tokens & keywords) > 0

def performer(items):
    pairs = []
    for key, value in pairs:
        if value in items.get(key, []):
            return True

    tokens = items['description_tokens']
    keywords = set(['musician', 'singer', 'song', 'songwriter', 'band', 'performer'])
    return len(tokens & keywords) > 0

def activist(items):
    pairs = []
    for key, value in pairs:
        if value in items.get(key, []):
            return True

    tokens = items['description_tokens']
    keywords = set(['activist'])
    return len(tokens & keywords) > 0


print "%50s" % ("Guest")
for idx,episode in enumerate(data):
    print "%(date)s, %(year)s" % episode

    for resource,pairs in episode['guest_predicate_objects'].items():
        print "%50s" % (resource),

        properties = pairs_to_dict(pairs)
        if politician(properties):
            print "Politician",
        if actor(properties):
            print "Actor",
        if comedian(properties):
            print "Comedian",
        if performer(properties):
            print "Performer",
        if activist(properties):
            print "Activist",
        if clergy(properties):
            print "Clergy",
        if business(properties):
            print "Business",
        if athlete(properties):
            print "Athlete",
        if writer(properties):
            print "Writer",
        if academic(properties):
            print "Academic",
        if journalist(properties):
            print "Journalist",

        print ""
