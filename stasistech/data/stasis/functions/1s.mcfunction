schedule function stasis:1s 1s replace

## Repeating logic not needing to be run every tick
# Enable datapack if Timelord has been acquired
execute unless score #enabled sts_vars matches 1 if score #salmeviradvancement bool matches 1 run function stasis:unlock
# Begin feature unlock dialog for player
execute if score #enabled sts_vars matches 1 as @a unless score @s sts_bool_seen_unlock_dialog matches 1.. at @s run function stasis:dialog/unlock_0
