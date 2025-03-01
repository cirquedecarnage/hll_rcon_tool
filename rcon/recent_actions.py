from collections import defaultdict
from logging import getLogger

from rcon.cache_utils import invalidates, ttl_cache
from rcon.logs.loop import on_kill, on_match_start, on_tk
from rcon.rcon import Rcon
from rcon.types import MostRecentEvents, StructuredLogLineWithMetaData

logger = getLogger(__name__)

RECENT_ACTIONS: defaultdict[str, MostRecentEvents] | None = None


# 2.5 hours is the max length of a HLL match (full 5 objective offensive round)
@ttl_cache(9000, is_method=False)
def get_recent_actions() -> defaultdict[str, MostRecentEvents]:
    global RECENT_ACTIONS
    if RECENT_ACTIONS is None:
        RECENT_ACTIONS = defaultdict(MostRecentEvents)

    return RECENT_ACTIONS


def set_recent_actions(recent_actions: defaultdict[str, MostRecentEvents]):
    global RECENT_ACTIONS
    with invalidates(get_recent_actions):
        RECENT_ACTIONS = recent_actions


@on_match_start
def reset_recent_actions(rcon: Rcon, struct_log):
    """Clear the event cache between rounds to prevent unbounded growing"""
    set_recent_actions(defaultdict(MostRecentEvents))


@on_kill
def update_kills(rcon: Rcon, log: StructuredLogLineWithMetaData):
    killer_name = log["player_name_1"]
    killer_player_id = log["player_id_1"]
    victim_name = log["player_name_2"]
    victim_player_id = log["player_id_2"]
    weapon = log["weapon"]

    if not killer_player_id or not victim_player_id:
        logger.error(
            "update_kills called with killer_player_id=%s victim_player_id=%s",
            killer_player_id,
            victim_player_id,
        )
        return

    cached_actions = get_recent_actions()
    killer = cached_actions[killer_player_id]
    victim = cached_actions[victim_player_id]

    killer.player_name = killer_name
    killer.last_victim_player_id = victim_player_id
    killer.last_victim_name = victim_name
    killer.last_victim_weapon = weapon

    victim.player_name = victim_name
    victim.last_nemesis_player_id = killer_player_id
    victim.last_nemesis_name = killer_name
    victim.last_nemesis_weapon = weapon

    set_recent_actions(cached_actions)
    # Refresh the redis cache so it's available for interprocess communication
    get_recent_actions()


@on_tk
def update_tks(rcon: Rcon, log: StructuredLogLineWithMetaData):
    killer_name = log["player_name_1"]
    killer_player_id = log["player_id_1"]
    victim_name = log["player_name_2"]
    victim_player_id = log["player_id_2"]
    weapon = log["weapon"]

    if not killer_player_id or not victim_player_id:
        logger.error(
            "update_kills called with killer_player_id=%s victim_player_id=%s",
            killer_player_id,
            victim_player_id,
        )
        return

    cached_actions = get_recent_actions()
    killer = cached_actions[killer_player_id]
    victim = cached_actions[victim_player_id]

    killer.player_name = killer_name
    killer.last_tk_victim_player_id = victim_player_id
    killer.last_tk_victim_name = victim_name
    killer.last_tk_victim_weapon = weapon

    victim.player_name = victim_name
    victim.last_tk_nemesis_player_id = killer_player_id
    victim.last_tk_nemesis_name = killer_name
    victim.last_tk_nemesis_weapon = weapon

    set_recent_actions(cached_actions)
    # Refresh the redis cache so it's available for interprocess communication
    get_recent_actions()
