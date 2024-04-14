-- discord_users
CREATE TABLE IF NOT EXISTS discord_users(
    user_id BIGINT PRIMARY KEY
);
ALTER TABLE discord_users ADD COLUMN IF NOT EXISTS name TEXT;
ALTER TABLE discord_users ADD COLUMN IF NOT EXISTS uploader BOOLEAN default FALSE;

-- discord_servers
CREATE TABLE IF NOT EXISTS discord_servers(
    server_id BIGINT PRIMARY KEY
);
ALTER TABLE discord_servers ADD COLUMN IF NOT EXISTS servername TEXT;
ALTER TABLE discord_servers ADD COLUMN IF NOT EXISTS language TEXT;
ALTER TABLE discord_servers ADD COLUMN IF NOT EXISTS play_maxlen INTEGER DEFAULT 0;

-- discord_user_displaynames
CREATE TABLE IF NOT EXISTS discord_user_displaynames(
    user_id BIGINT NOT NULL,
    server_id BIGINT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES discord_users (user_id),
    FOREIGN KEY (server_id) REFERENCES discord_servers (server_id),
    PRIMARY KEY (user_id,server_id)
);
ALTER TABLE discord_user_displaynames ADD COLUMN IF NOT EXISTS displayname TEXT NOT NULL default 'unknown_user';

-- discord_server_admin_groups
CREATE TABLE IF NOT EXISTS discord_server_admin_groups(
    server_id BIGINT NOT NULL,
    group_name TEXT NOT NULL,
    FOREIGN KEY (server_id) REFERENCES discord_servers (server_id),
    PRIMARY KEY (server_id,group_name)
);

-- files
CREATE TABLE IF NOT EXISTS files(
    file_id BIGINT PRIMARY KEY,
    file_size BIGINT,
    server_id BIGINT,
    uploader_id BIGINT,
    display_name TEXT NOT NULL,
    file_name TEXT NOT NULL,
    hash TEXT NOT NULL,
    public BOOLEAN,
    FOREIGN KEY (server_id) REFERENCES discord_servers (server_id),
    FOREIGN KEY (uploader_id) REFERENCES discord_users (user_id)
);

-- tags
CREATE TABLE IF NOT EXISTS tags(
    tag_id BIGINT PRIMARY KEY,
    tag_name TEXT NOT NULL
);

-- files_tags
CREATE TABLE IF NOT EXISTS files_tags(
    file_id BIGINT,
    tag_id BIGINT,
    FOREIGN KEY (file_id) REFERENCES files,
    FOREIGN KEY (tag_id) REFERENCES tags,
    PRIMARY KEY (file_id,tag_id)
);
