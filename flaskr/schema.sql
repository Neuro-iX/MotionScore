DROP TABLE IF EXISTS user;

DROP TABLE IF EXISTS volume;

DROP TABLE IF EXISTS score;

CREATE TABLE
    user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_code TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE
    );

CREATE TABLE
    volume (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sub_id TEXT NOT NULL,
        ses_id TEXT NOT NULL,
        volume_path TEXT NOT NULL,
        dataset TEXT NOT NULL
    );

CREATE TABLE
    review (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        judge_code TEXT NOT NULL,
        vol_id INTEGER NOT NULL,
        score INTEGER NOT NULL,
        lines BOOLEAN DEFAULT False,
        blur BOOLEAN DEFAULT False,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (vol_id) REFERENCES volume (id),
        FOREIGN KEY (judge_code) REFERENCES user (user_code)
    );