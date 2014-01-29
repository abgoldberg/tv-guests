import sys
import csv
import sqlite3

def get_dicts(inputfile):
    with open(inputfile, 'rb') as csvfile:
        return list(csv.DictReader(csvfile))

mapping = {
    1: "Academic",
    2: "Actor",
    3: "Athlete",
    4: "Business",
    5: "Clergy",
    6: "Comedian",
    7: "Journalist",
    8: "Musician",
    9: "Policy",
    10: "Politician",
    11: "Writer",
    12: "Other"
    }

def update_db(dicts, cursor):
    for row in dicts:
        coded_label = int(row['Guest_Category'])
        label = mapping[coded_label]
        print "%s: %s: %s" % (row['AppearanceID'], row['GuestResource'], label)
        cursor.execute("INSERT INTO labels (aid, label, source, confidence) VALUES (:aid, :label, :source, :confidence)",
                       { 'aid': row['AppearanceID'], 'label': label, 'confidence': 1.0, 'source': 'amy' })

if __name__=="__main__":
    csvfile = sys.argv[1]

    dicts = get_dicts(csvfile)

    db_file = sys.argv[2]
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    update_db(dicts, cursor)

    conn.commit()
