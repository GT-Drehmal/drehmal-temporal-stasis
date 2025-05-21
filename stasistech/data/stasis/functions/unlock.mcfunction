## Unlocks Temporal Stasis features for all players, and gifts them the initial hourglass & recipes
scoreboard players set #enabled sts_vars 1
# Reset hourglass reception
scoreboard objectives remove sts_bool_received_hourglass
scoreboard objectives add sts_bool_received_hourglass dummy
# [Hard-coded] Base max claims count
lp group default meta set xaero.pac_max_claims 32