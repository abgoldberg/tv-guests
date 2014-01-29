#!/usr/bin/python
import sqlite3
import sqlite3_addon
import json
import cgi
import cgitb
cgitb.enable()

def main(group_by_category=False):
    print "Content-Type: text/plain;charset=utf-8"
    print

    db_file = "guests.dat"
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3_addon.dict_factory
    cursor = conn.cursor()

    if group_by_category:
        select = "SELECT label AS description, show, label, count(*) as frequency FROM episodes JOIN appearances USING (eid) JOIN guests USING (resource) JOIN labels USING (aid) WHERE source = 'amy' GROUP BY label, show ORDER BY resource;"
    else:
        select = "SELECT resource AS description, show, label, count(label) as frequency FROM episodes JOIN appearances USING (eid) JOIN guests USING (resource) JOIN labels USING (aid) WHERE source = 'amy' GROUP BY resource, show ORDER BY resource;"

    cursor.execute(select)
    rows = cursor.fetchall()

    data = {}
    for row in rows:
        desc = row['description']
        if desc not in data:
            data[desc] = {}
        data[desc][row['show']] = (row['label'], row['frequency'])

    MIN_COUNT = 0 if group_by_category else 5

    output = []
    for desc, show_data in data.items():
        if 'tds' in show_data:
            label = show_data['tds'][0]
            tds_count = show_data['tds'][1]
        else:
            tds_count = 0

        if 'colbert' in show_data:
            label = show_data['colbert'][0]
            colbert_count = show_data['colbert'][1]
        else:
            colbert_count = 0

        if tds_count + colbert_count >= MIN_COUNT:
            output.append({'description':desc, 'label': label, 'tds': tds_count, 'colbert': colbert_count})

    print json.dumps(output)

if __name__=="__main__":

    form = cgi.FieldStorage()
    if 'group_by_category' in form:
        group_by_category = form['group_by_category'].value == "1"
    else:
        group_by_category = False

    main(group_by_category=group_by_category)
