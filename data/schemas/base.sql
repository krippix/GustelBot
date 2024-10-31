-- discord_users
create table if not exists discord_users(
    user_id bigint primary key
);
alter table discord_users add column if not exists name text;
alter table discord_users add column if not exists uploader boolean default false;

-- discord_servers
create table if not exists discord_servers(
    server_id bigint primary key
);
alter table discord_servers add column if not exists servername text;
alter table discord_servers add column if not exists language text;
alter table discord_servers add column if not exists play_maxlen integer default 0;

-- discord_user_displaynames
create table if not exists discord_user_displaynames(
    user_id bigint not null,
    server_id bigint not null,
    foreign key (user_id) references discord_users (user_id),
    foreign key (server_id) references discord_servers (server_id),
    primary key (user_id,server_id)
);
alter table discord_user_displaynames add column if not exists displayname text not null default 'unknown_user';

-- discord_server_admin_groups
create table if not exists discord_server_admin_groups(
    server_id bigint not null,
    group_name text not null,
    foreign key (server_id) references discord_servers (server_id),
    primary key (server_id,group_name)
);

-- files
create table if not exists files(
    file_id bigserial primary key,
    file_size bigint,
    server_id bigint,
    uploader_id bigint,
    display_name text not null,
    file_name text not null,
    file_hash text not null,
    public boolean,
    foreign key (server_id) references discord_servers (server_id),
    foreign key (uploader_id) references discord_users (user_id)
);
alter table files add column if not exists seconds bigint;
alter table files add column if not exists deleted boolean default false not null;
alter table files add column if not exists deletion_date timestamp;

-- tags
create table if not exists tags(
    tag_id bigserial primary key,
    tag_name text not null unique
);

-- files_tags
create table if not exists files_tags(
    file_id bigint,
    tag_id bigint,
    foreign key (file_id) references files,
    foreign key (tag_id) references tags,
    primary key (file_id,tag_id)
);
