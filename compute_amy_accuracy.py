import sys
import csv

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

def compute_baseline(dicts):
    counts = {}
    total = 0
    for row in dicts:
        coded_label = int(row['Guest_Category'])
        label = mapping[coded_label]
        counts[label] = counts.get(label, 0) + 1
        total += 1

    sum = 0
    for label,count in counts.items():
        p = float(count)/total
        print label
        print p
        sum += p*p

    print "Sum: %f" % sum

def compute_accuracy(dicts, source=None):
    total_count = 0
    correct_count = 0

    total_guest_count = 0
    correct_guest_count = 0

    seen = {}
    #sources = {}
    incorrect_labels = {}

    for row in dicts:
        #print row['GuestResource'].strip()
        #print row

        coded_label = int(row['Guest_Category'])
        label = mapping[coded_label]

        row_source = row['LabelSource'].strip()

        #sources[row_source] = 1

        if source is not None and row_source != source:
            continue

        scores = {}
        for code,category in mapping.items():
            if category in row:
                scores[category] = float(row[category])

        max_predicted_score = max(scores.values())

        truth_score = scores[label] if label in scores else -1 # incorrect if Other

        correct = (max_predicted_score == truth_score)

        if False and total_count < 20:
            print ""
            print row['GuestResource'].strip()
            print "True label: %s" % label
            print "Max predicted score: %s" % max_predicted_score
            print "Score predicted for true label: %s" % truth_score
            print "Correct: %s" % correct
            print scores

        total_count += 1
        correct_count += correct

        if not correct:
            incorrect_labels[label] = incorrect_labels.get(label,0) + 1

        if row['GuestResource'] not in seen:
            total_guest_count += 1
            correct_guest_count += correct
            seen[row['GuestResource']] = True

    print ""
    print "%s: %d appearances, %d correct" % (source, total_count, correct_count)
    print "Appearance-level Accuracy: %s" % (float(correct_count) / total_count)

    #print "%s: %d guests, %d correct" % (source, total_guest_count, correct_guest_count)
    #print "Guest-level Accuracy: %s" % (float(correct_guest_count) / total_guest_count)

    print incorrect_labels

    #print sources

if __name__=="__main__":
    csvfile = sys.argv[1]

    dicts = get_dicts(csvfile)

    compute_accuracy(dicts, 'heuristics')
    compute_accuracy(dicts, 'classifier')
    compute_accuracy(dicts)

    compute_baseline(dicts)
