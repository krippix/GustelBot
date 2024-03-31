-- discord_users
CREATE TABLE IF NOT EXISTS discord_users(
    user_id BIGINT PRIMARY KEY
);
ALTER TABLE discord_users ADD COLUMN IF NOT EXISTS name TEXT;

-- discord_servers
CREATE TABLE IF NOT EXISTS discord_servers(
    server_id BIGINT PRIMARY KEY
);
ALTER TABLE discord_servers ADD COLUMN IF NOT EXISTS servername TEXT;
ALTER TABLE discord_servers ADD COLUMN IF NOT EXISTS language TEXT;

-- discord_user_displaynames
CREATE TABLE IF NOT EXISTS discord_user_displaynames(
    user_id BIGINT NOT NULL,
    server_id BIGINT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES discord_users (user_id),
    FOREIGN KEY (server_id) REFERENCES discord_servers (server_id),
    PRIMARY KEY (user_id,server_id)
);
ALTER TABLE discord_user_displaynames ADD COLUMN IF NOT EXISTS displayname TEXT NOT NULL;