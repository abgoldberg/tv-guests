import sys
import json
import sqlite3
from dateutil import parser
import dbpedia
import rdflib

import logging
global LOG_CONFIG
LOG_CONFIG = { 'level': logging.DEBUG }
try:
    import log
except ImportError:
    pass

# Script scans guests.dat for guests without dbpedia data
# and adds it where possible.

if __name__=="__main__":
    conn = sqlite3.connect('guests.dat')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT resource FROM guests WHERE dbpedia IS NULL")
    rows = cursor.fetchall()
    for row in rows:
        resource = row['resource']
        log.info("Need dbpedia data for %s", resource)

        (g,name) = dbpedia.lookup(resource)
        res = rdflib.URIRef('http://dbpedia.org/resource/%s' % name)

        predicate_objects = []
        for (p, o) in g.predicate_objects(res):
            predicate_objects.append((p,o))

        cursor.execute("UPDATE guests SET dbpedia = :dbpedia WHERE resource = :resource",
                       { "resource": resource, "dbpedia": json.dumps(predicate_objects) })

        log.info("Added dbpedia data for %s", resource)

    conn.commit()
