import sys
import re
import string
import json
import time
import types
import sqlite3

import logging
global LOG_CONFIG
LOG_CONFIG = { 'level': logging.DEBUG }
try:
    import log
except ImportError:
    pass

def print_appearances(cursor):

    print "Show, Airdate, AppearanceID, GuestResource, LabelSource,",
    cursor.execute("SELECT label FROM labels GROUP BY label ORDER BY label")
    label_rows = cursor.fetchall()
    labels = [lrow['label'] for lrow in label_rows]
    print ", ".join(labels)

    cursor.execute("SELECT show, date(airdate) as airdate, eid, aid, resource FROM episodes " +
                   "JOIN appearances USING (eid) " +
                   "JOIN guests USING (resource) " +
                   "ORDER BY airdate")

    rows = cursor.fetchall()
    for row in rows:
        cursor.execute("SELECT label, confidence, source FROM labels WHERE aid = :aid ORDER BY label", { 'aid': row['aid'] })
        label_rows = cursor.fetchall()

        print "%(show)s, %(airdate)s, %(aid)s, %(resource)s," % dict(row),
        print label_rows[0]['source'] + ",",

        label_dict = {label:0 for label in labels}
        for lrow in label_rows:
            label_dict[lrow['label']] = round(lrow['confidence'],2)

        print ", ".join(["%g" % label_dict[label] for label in labels])

if __name__=="__main__":
    db_file = sys.argv[1]
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print_appearances(cursor)
