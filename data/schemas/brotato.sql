-- brotato_chars
CREATE TABLE IF NOT EXISTS brotato_chars(
    char_id SERIAL PRIMARY KEY
);
ALTER TABLE brotato_chars ADD COLUMN IF NOT EXISTS name_en TEXT;
ALTER TABLE brotato_chars ADD COLUMN IF NOT EXISTS name_de TEXT;

-- brotato_runs
CREATE TABLE IF NOT EXISTS brotato_runs(
    FOREIGN KEY (user_id) REFERENCES discord_users (user_id),
    FOREIGN KEY (server_id) REFERENCES discord_servers (server_id),
    FOREIGN KEY (char_id) REFERENCES brotato_chars (char_id)
);
ALTER TABLE brotato_runs ADD COLUMN IF NOT EXISTS run_id SERIAL PRIMARY KEY;
ALTER TABLE brotato_runs ADD COLUMN IF NOT EXISTS user_id BIGINT NOT NULL;
ALTER TABLE brotato_runs ADD COLUMN IF NOT EXISTS server_id BIGINT;
ALTER TABLE brotato_runs ADD COLUMN IF NOT EXISTS char_id SMALLINT NOT NULL;
ALTER TABLE brotato_runs ADD COLUMN IF NOT EXISTS wave SMALLINT NOT NULL;
ALTER TABLE brotato_runs ADD COLUMN IF NOT EXISTS danger SMALLINT NOT NULL;
ALTER TABLE brotato_runs ADD COLUMN IF NOT EXISTS timestamp INTEGER;
