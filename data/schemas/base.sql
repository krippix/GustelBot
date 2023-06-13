CREATE TABLE IF NOT EXISTS discord_users (
    user_id BIGINT PRIMARY KEY,
    name TEXT
);
CREATE TABLE IF NOT EXISTS discord_servers (
    server_id BIGINT PRIMARY KEY,
    servername TEXT,
    language TEXT
);
CREATE TABLE IF NOT EXISTS discord_user_displaynames (
    user_id BIGINT NOT NULL,
    server_id BIGINT NOT NULL,
    displayname TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES discord_users (user_id),
    FOREIGN KEY (server_id) REFERENCES discord_servers (server_id),
    PRIMARY KEY (user_id,server_id)
);