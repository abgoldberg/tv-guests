# Older code using CSV file of guests and checking only dbpedia for meta data

import sys

import logging
#logging.basicConfig(filename='python.log')

import load_csv
import dbpedia

PROPS = set(['occupation', 'shortDescription', 'description', 'title'])

def main(inputfile, year):
    people = {}
    dicts = load_csv.get_dicts(inputfile)
    count = 0
    for d in dicts:
        query = d['title']

        if year and not d['airdate'].endswith(year):
            continue

        if "Episode" in query:
            continue
        else:
            print '\n'

            if query not in people:
                try:
                    (g,name) = dbpedia.lookup(query)
                    people[query] = dbpedia.get_properties(g, name)
                except UnicodeEncodeError:
                    logging.exception("caught exception looking up %s", query)
                    name = d['title']
                    people[query] = {}

                people[query]['__name'] = name.replace('_', ' ')

            properties = people[query]
            d['name'] = properties['__name']

            if d['name'] != d['title']:
                print "%(airdate)s %(title)s (resolved to %(name)s)" % (d)
            else:
                print "%(airdate)s %(title)s" % (d)

            properties['target_count'] = 0
            properties['properties_found'] = len(properties)
            for k,v in properties.items():
                if k in PROPS:
                    print "\t\t%20s\t%s" % (k,', '.join(v))
                    properties['target_count'] += 1

        count += 1
        #if count > 20:
        #    break

    print "\n\nCould not find any target properties for:\n"
    for query,properties in people.items():
        if properties['target_count'] == 0:
            print "%30s %2d total properties found" % (query, properties['properties_found'])

if __name__=="__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
