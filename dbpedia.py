import sys
import rdflib
import wikipedia
import urllib

def lookup(input, search=True, redirect=False):
    query = input.replace(' ', '_')

    g=rdflib.Graph()
    g.load('http://dbpedia.org/resource/%s' % query)

    if len(g) == 0 and search:
        results = wikipedia.search(input)
        if len(results) > 0:
            input = results[0]

            input = encode(input)
            (g, query) = lookup(input, search=False)
            query = decode(query)

            return (g, query)
    elif not redirect:
        # Check for redirects
        for s,p,o in g:
            if str(p) == "http://dbpedia.org/ontology/wikiPageRedirects":
                return lookup(o.split('/')[-1], redirect=True)

    return (g, query)

# Hackery to get rdflib to retrieve pages with unicode in names
def encode(input):
    if isinstance(input, unicode):
        input = input.encode('utf-8')
    input = urllib.quote(input)
    input = input.replace('%20', '_')
    return input

# Reverse the above hackery
def decode(query):
    query = urllib.unquote(query)
    if isinstance(input, unicode):
        query = query.encode('utf-8')
    return query

def get_properties(g, query):
    query = encode(query)
    props = {}
    for s,p,o in g:
        if res(s) == query and p.startswith('http://dbpedia.org/property/'):
            p = prop(p)
            if p not in props:
                props[p] = []
            props[p].append(res(o))
    return props

def print_properties(g, query):
    query = encode(query)
    for s,p,o in g:
        if p.startswith('http://dbpedia.org/property/'):
            if res(s) == query:
                print "%20s\t%20s\t%20s" % (res(s),prop(p),res(o))

    for s,p,o in g:
        if p.startswith('http://dbpedia.org/property/'):
            if 'episodes' in res(s):
                print "%20s\t%20s\t%20s" % (res(s),prop(p),res(o))

def res(p):
    return p.replace('http://dbpedia.org/resource/', '')

def prop(p):
    return p.replace('http://dbpedia.org/property/', '')

if __name__=="__main__":
    (g, name) = lookup(' '.join(sys.argv[1:]))
    print_properties(g, name)

    for s,p,o in g:
        print s,p,o
