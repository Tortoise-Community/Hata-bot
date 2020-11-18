import json
from . import models

async def post_infraction(
    client, 
    *, 
    guild_id, 
    target_id, 
    moderator_id, 
    reason, 
    case_type, 
    extras=None, 
    cross_guild=False, 
    pardoned=False
):
    if extras is None:
        extras = {}
    extras = json.dumps(extras)
    conn = client.database.conn
    lock = client.database.lock
    execute = """
        INSERT INTO moderation(
            guild_id, target_id,
            moderator_id, reason,
            case_type, extras, 
            cross_guild, pardoned
        ) VALUES (
            $1, $2, $3, $4, $5, 
            $6, $7, $8
        ) RETURNING *
    """
    async with lock:
        data = await conn.fetch(
            execute, str(guild_id), 
            str(target_id), str(moderator_id),
            reason, case_type, extras, 
            cross_guild, pardoned
        )
    return models.Infraction(client, data[0])

async def pardon_infraction(client, *, guild_id, target_id, moderator_id, reason, case_number):
    conn = client.database.conn
    lock = client.database.lock
    execute = """
        UPDATE moderation SET
            pardoned = $1
        WHERE 
            case_number = $2
    """
    extras = json.dumps({'pardoned_case': case_number})
    async with lock:
        await conn.execute(execute, True, case_number)
    infraction = await post_infraction(
        client, 
        guild_id=guild_id, 
        target_id=target_id, 
        moderator_id=moderator_id, 
        reason=reason, 
        case_type='pardon', 
        extras=extras, 
        cross_guild=None, 
        pardoned=None
    )
    return infraction

async def get_infraction(client, *, case_number):
    execute = """
        SELECT * FROM moderation WHERE
            case_number = $1
    """
    conn = client.database.conn
    lock = client.database.lock
    async with lock:
        data = await conn.fetch(execute, case_number)
    if data:
        return models.Infraction(client, data[0])


async def get_infractions_for_target(client, *, target_id):
    execute = """
        SELECT * FROM moderation WHERE
            target_id = $1
    """
    conn = client.database.conn
    lock = client.database.lock
    async with lock:
        data = await conn.fetch(execute, str(target_id))
    return [models.Infraction(client, d) for d in data]

async def get_infractions_for_target_in_guild(client, *, guild_id, target_id):
    execute = """
        SELECT * FROM moderation WHERE
            target_id = $1
                AND
            guild_id = $2
    """
    conn = client.database.conn
    lock = client.database.lock
    async with lock:
        data = await conn.fetch(execute, str(target_id), str(guild_id))
    return [models.Infraction(client, d) for d in data]

async def get_infractions_by_moderator(client, *, moderator_id):
    execute = """
        SELECT * FROM moderation WHERE
            moderator_id = $1
    """
    conn = client.database.conn
    lock = client.database.lock
    async with lock:
        data = await conn.fetch(execute, str(moderator_id))
    return [models.Infraction(client, d) for d in data]

async def get_infractions_by_moderator_in_guild(client, *, guild_id, moderator_id):
    execute = """
        SELECT * FROM moderation WHERE
            moderator_id = $1
                AND
            guild_id = $2
    """
    conn = client.database.conn
    lock = client.database.lock
    async with lock:
        data = await conn.fetch(execute, str(moderator_id), str(guild_id))
    return [models.Infraction(client, d) for d in data]

async def get_infractions_in_guild(client, *, guild_id):
    execute = """
        SELECT * FROM moderation WHERE
            guild_id = $2
    """
    conn = client.database.conn
    lock = client.database.lock
    async with lock:
        data = await conn.fetch(execute, str(guild_id))
    return [models.Infraction(client, d) for d in data]

async def delete_infraction(client, *, case_number):
    execute = """
        DELETE FROM moderation WHERE
            case_number = $1
    """
    conn = client.database.conn
    lock = client.database.lock
    async with lock:
        await conn.execute(execute, case_number)

async def post_guild_setup(
    client,
    *,
    guild_id,
    log_channel_id=None,
    muted_role_id=None,
    disabled_commands=None,
    prefixes=None,
    level_roles=None,
    join_roles=None
):
    if log_channel_id is not None:
        log_channel_id = str(log_channel_id)
    if muted_role_id is not None:
        muted_role_id = str(muted_role_id)
    if disabled_commands is None:
        disabled_commands = []
    if prefixes is None:
        prefixes = ['!']
    if level_roles is None:
        level_roles = {}
    if join_roles is None:
        join_roles = []
    conn = client.database.conn
    lock = client.database.lock
    execute = """
        INSERT INTO guilds (
            guild_id, log_channel_id,
            muted_role_id, disabled_commands,
            prefixes, level_roles,
            join_roles
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7
        )
    """
    async with lock:
        await conn.execute(
            execute, 
            str(guild_id), 
            log_channel_id,
            muted_role_id,
            json.dumps(disabled_commands),
            json.dumps(prefixes),
            json.dumps(level_roles),
            json.dumps(join_roles)
        )

async def update_guild_setup(
    client,
    *,
    guild_id,
    log_channel_id=None,
    muted_role_id=None,
    disabled_commands=None,
    prefixes=None,
    level_roles=None,
    join_roles=None
):
    params = {}
    if log_channel_id is not None:
        params['log_channel_id'] = str(log_channel_id)
    if muted_role_id is not None:
        params['muted_role_id'] = str(muted_role_id)
    if disabled_commands is not None:
        params['disabled_commands'] = json.dumps(disabled_commands)
    if prefixes is not None:
        params['prefixes'] = json.dumps(prefixes)
    if level_roles is not None:
        params['level_roles'] = json.dumps(level_roles)
    if join_roles is not None:
        params['join_roles'] = json.dumps(join_roles)
    execute = 'UPDATE guilds SET ' + ''.join((k + ' = $%s' % i) + (', ' if i < len(params) else ' ') for i, k in enumerate(params, start=1)) + ('WHERE guild_id = $%s' % (len(params) + 1))
    conn = client.database.conn
    lock = client.database.lock
    async with lock:
        await conn.execute(execute, *params.values(), str(guild_id))

async def delete_guild_setup(client, *, guild_id):
    execute = """
        DELETE FROM guilds WHERE
            guild_id = $1
    """
    conn = client.database.conn
    lock = client.database.lock
    async with lock:
        await conn.execute(execute, str(guild_id))

async def get_guild_setup(client, *, guild_id):
    execute = """
        SELECT * FROM guilds WHERE
            guild_id = $1
    """
    conn = client.database.conn
    lock = client.database.lock
    async with lock:
        data = await conn.fetch(execute, str(guild_id))
    if data:
        return dict(data[0])