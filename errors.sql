CREATE TABLE entries (
    date          DATETIME,
    severity      TEXT,
    msgID         TEXT,
    application   TEXT,
    host          TEXT,
    text          TEXT,
    sb            BIT, 
    sb_total_time REAL,
    sb_time_run   REAL,
    sb_length     REAL,
    run           REAL,
    gh            INTEGER PRIMARY KEY,
    CONSTRAINT unique_gh UNIQUE(gh)
);
