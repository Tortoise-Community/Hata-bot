CREATE TABLE IF NOT EXISTS guilds (
    guild_id CHARACTER VARYING PRIMARY KEY,
    log_channel_id CHARACTER VARYING,
    muted_role_id CHARACTER VARYING,
    disabled_commands JSON NOT NULL,
    prefixes JSON NOT NULL,
    level_roles JSON NOT NULL, 
    join_roles JSON NOT NULL
);

CREATE TABLE IF NOT EXISTS moderation (
    case_number SERIAL PRIMARY KEY,
    target_id CHARACTER VARYING NOT NULL,
    guild_id CHARACTER VARYING NOT NULL,
    moderator_id CHARACTER VARYING NOT NULL,
    reason CHARACTER VARYING NOT NULL,
    case_type CHARACTER VARYING NOT NULL,
    extras JSON,
    pardoned BOOLEAN,
    cross_guild BOOLEAN
);