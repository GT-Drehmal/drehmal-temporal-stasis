# Undo unlock.mcfunction
scoreboard players reset #enabled sts_vars
scoreboard players reset @a sts_bool_received_hourglass
scoreboard players reset @a sts_bool_seen_unlock_dialog
lp group default meta set xaero.pac_max_claims 0