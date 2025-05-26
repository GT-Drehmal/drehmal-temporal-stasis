# Number of claims a player currently has
scoreboard objectives add sts_claims dummy
# If the player has already been given the initial hourglass
scoreboard objectives add sts_bool_received_hourglass dummy
# [Hard-coded] Base maximum claim capacity for every player
scoreboard players set #max sts_claims 32
# A player's claim capacity is increased by this much on top of #max:
scoreboard objectives add sts_extra_claims dummy
scoreboard objectives add sts_temp dummy
scoreboard objectives add sts_vars dummy
scoreboard players set #nodrehmal? sts_vars 0
# Item usage
scoreboard objectives add sts_click minecraft.used:warped_fungus_on_a_stick
scoreboard objectives add sts_throw_potion minecraft.used:splash_potion
scoreboard objectives add sts_use_pearl minecraft.used:ender_pearl
## Triggers
scoreboard objectives add sts_tg_get_remaining trigger
scoreboard objectives add sts_tg_get_recipe_hourglass trigger
scoreboard objectives add sts_tg_get_recipe_bubble trigger

## Scheduled
schedule function stasis:1s 1s replace

# ===============
## Uncomment this only if you're trying to run this without the Drehmal datapack active.
## Note this may cause unexpected bugs to occur. Use for testing purposes only.
# say "[Stasis claim] Non-Drehmal mode is active"
# scoreboard players set #nodrehmal? sts_vars 1
# ===============

say [Stasis claim] Load success
execute unless score #enabled sts_vars matches 1 run tellraw @s "[Stasis claim] Note: Stasis is not enabled"