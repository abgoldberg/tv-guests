import json
import dbpedia
import rdflib
import time
import sys

#input_file = 'scrapy_tds/items.json'
input_file = sys.argv[1]

data = json.load(open(input_file))

print "Loaded %s episodes of data from %s" % (len(data), input_file)

output_file = '%s.extended' % (input_file)

print "Will write extended json to %s" % (output_file)

raw_input("Press Enter to continue...")

for idx,episode in enumerate(data):
    print "Processing episode\n\t%s" % (episode)

    episode['guest_predicate_objects'] = {}
    for resource in episode['guest_resources']:
        (g,name) = dbpedia.lookup(resource)
        res = rdflib.URIRef('http://dbpedia.org/resource/%s' % name)

        # Augment the episode entry with the predicates and objects of the current resource
        p_o = episode['guest_predicate_objects'][resource] = []
        for (p, o) in g.predicate_objects(res):
            p_o.append((p,o))

        print "Augmented episode with %s predicate-object pairs about %s" % (len(p_o), resource)
    print ""

    time.sleep(0.2) # don't hammer too hard

# Write the augmented json back to a file
with open(output_file, 'w') as outfile:
    outfile.write(json.dumps(data, indent=4))

