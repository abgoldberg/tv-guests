CREATE TABLE episodes (
       eid TEXT PRIMARY KEY,
       show TEXT,
       airdate DATETIME,
       month_day TEXT,
       year TEXT,
       promotion TEXT);

CREATE TABLE appearances (
       aid INTEGER PRIMARY KEY,
       eid INTEGER REFERENCES episodes(eid),
       resource TEXT REFERENCES guests(resource));

CREATE TABLE guests (
       resource TEXT PRIMARY KEY,
       dbpedia TEXT);

CREATE TABLE labels (
       aid INTEGER REFERENCES appearances(aid),
       label TEXT,
       source TEXT,
       confidence NUMERIC DEFAULT 1.0);