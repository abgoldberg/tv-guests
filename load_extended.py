import sys
import json
import sqlite3
from dateutil import parser

import logging
global LOG_CONFIG
LOG_CONFIG = { 'level': logging.DEBUG }
try:
    import log
except ImportError:
    pass

if __name__=="__main__":
    show = sys.argv[1]
    json_file = sys.argv[2]
    data = json.load(open(json_file))

    conn = sqlite3.connect('guests.dat')
    cursor = conn.cursor()

    for episode in data:
        #log.debug("episode = %s", episode)

        # cleanup mysterious unicode characters
        episode['date'] = episode['date'].replace(u'\u2020', '')
        date_string = "%s, %s" % (episode['date'], episode['year']) if ", %s" % episode['year'] not in episode['date'] else episode['date']
        airdate = parser.parse(date_string)
        eid = "%s-%s" % (show, airdate)
        values = {
            'eid': eid,
            'show': show,
            'airdate': airdate,
            'month_day': episode['date'],
            'year': episode['year'],
            'promotion': episode['promotion']
            }

        # Check if we have any data for this episode in the database yet
        cursor.execute("SELECT eid FROM episodes WHERE eid = :eid", { "eid": eid})
        rows = cursor.fetchall()
        if len(rows) != 0:
            for resource, predicate_objects in episode.get('guest_predicate_objects', {}).items():
                # Check if we already have dbpedia data for this guest
                cursor.execute("SELECT dbpedia FROM guests WHERE resource = :resource AND dbpedia IS NOT NULL",
                               { "resource": resource })
                rows = cursor.fetchall()
                if len(rows) == 0:
                    cursor.execute("UPDATE guests SET dbpedia = :dbpedia WHERE resource = :resource",
                                   { "resource": resource, "dbpedia": json.dumps(predicate_objects) })
                    log.info("Added dbpedia data for %s", resource)
                else:
                    log.info("Already have dbpedia data for %s", resource)
        else:
            log.info("Don't have episode %s in the database", eid)

    conn.commit()
