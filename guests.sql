CREATE TABLE episodes (
       eid TEXT PRIMARY KEY,
       show TEXT,
       airdate DATETIME,
       month_day TEXT,
       year TEXT,
       promotion TEXT);
CREATE TABLE appearances (
       eid INTEGER REFERENCES episodes(eid),
       resource TEXT,
       dbpedia TEXT,
       heuristic_labels TEXT,
       ssl_labels TEXT,
       manual_labels TEXT);