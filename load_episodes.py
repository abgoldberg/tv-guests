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

    added = 0
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

        cursor.execute("SELECT eid FROM episodes WHERE eid = :eid", { "eid": eid})
        rows = cursor.fetchall()
        if len(rows) == 0:
            cursor.execute("INSERT INTO episodes (eid, show, airdate, month_day, year, promotion)" + \
                               " VALUES (:eid, :show, :airdate, :month_day, :year, :promotion)", values)

            log.info("Added episode %s to the database", eid)
            added += 1

            for resource in episode.get('guest_resources', []):
                # Add guest row if necessary
                cursor.execute("SELECT resource FROM guests WHERE resource = :resource",
                               {"resource": resource})
                rows = cursor.fetchall()
                if len(rows) == 0:
                    cursor.execute("INSERT OR IGNORE INTO guests (resource) VALUES (:resource)",
                                   {"resource": resource})
                    log.info("Added row for guest %s", resource)
                else:
                    log.info("Already have row for guest %s", resource)

                cursor.execute("INSERT INTO appearances (eid, resource) VALUES (:eid, :resource)",
                               { "eid": eid, "resource": resource })
                log.info("Added appearance for %s for episode %s", resource, eid)
        else:
            log.info("Already have episode %s in the database", eid)

    conn.commit()
    log.info("Added %d episodes to the database", added)
