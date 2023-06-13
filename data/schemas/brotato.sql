CREATE TABLE IF NOT EXISTS brotato_chars (
    char_id SERIAL PRIMARY KEY,
    name_en TEXT,
    name_de TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS brotato_runs (
    run_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    server_id BIGINT,
    char_id SMALLINT NOT NULL,
    wave SMALLINT NOT NULL,
    danger SMALLINT NOT NULL,
    timestamp INTEGER,
    FOREIGN KEY (user_id) REFERENCES discord_users (user_id),
    FOREIGN KEY (server_id) REFERENCES discord_servers (server_id),
    FOREIGN KEY (char_id) REFERENCES brotato_chars (char_id)
);
