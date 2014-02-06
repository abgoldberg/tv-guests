#!/usr/bin/python
import sqlite3
import sqlite3_addon
import json
import cgi
import cgitb
cgitb.enable()

def main(show, category):
    print "Content-Type: text/plain;charset=utf-8"
    print

    db_file = "guests.dat"
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3_addon.dict_factory
    cursor = conn.cursor()

    if show != "combined":
        select = "SELECT strftime('%s', airdate) as timestamp, count(*) as frequency FROM episodes JOIN appearances USING (eid) JOIN guests USING (resource) JOIN labels USING (aid) WHERE source = 'amy' AND show = ? AND label = ? GROUP BY timestamp ORDER BY timestamp;"
        cursor.execute(select, (show, category))
    else:
        select = "SELECT strftime('%s', airdate) as timestamp, count(*) as frequency FROM episodes JOIN appearances USING (eid) JOIN guests USING (resource) JOIN labels USING (aid) WHERE source = 'amy' AND label = ? GROUP BY timestamp ORDER BY timestamp;"
        cursor.execute(select, (category,))

    rows = cursor.fetchall()

    output = {}
    for row in rows:
        output[row['timestamp']] = row['frequency']

    print json.dumps(output)

if __name__=="__main__":

    form = cgi.FieldStorage()
    show = form['show'].value
    if 'category' in form:
        category = form['category'].value
    else:
        category = 'Politician'

    main(show, category)
