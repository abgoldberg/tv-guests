CREATE TABLE episodes (
       eid TEXT PRIMARY KEY,
       show TEXT,
       airdate DATETIME,
       month_day TEXT,
       year TEXT,
       promotion TEXT);
CREATE TABLE appearances (
       eid INTEGER REFERENCES episodes(eid),
       resource TEXT REFERENCES guests(resource),
       heuristic_labels TEXT,
       ssl_labels TEXT,
       manual_labels TEXT);
CREATE TABLE guests (
       resource TEXT PRIMARY KEY,
       dbpedia TEXT);