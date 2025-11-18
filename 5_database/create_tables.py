CREATE TABLE creators (
    creator_id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    platform VARCHAR(50),
    bio_text TEXT,
    UNIQUE(username, platform)
);