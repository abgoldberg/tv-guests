import sys
import csv

def get_dicts(inputfile):
    with open(inputfile, 'rb') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        rows = csv.DictReader(csvfile, dialect=dialect)
        return list(rows)

if __name__=="__main__":
    dicts = get_dicts(sys.argv[1])
    for d in dicts:
            print "%(airdate)s: %(title)s" % (d)
