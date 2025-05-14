# No. of claims a player currently has
scoreboard objectives add sts_claims dummy
# Base maximum claim capacity for every player
scoreboard players set #max sts_claims 32
# A player's claim capacity is increased by this much on top of #max:
scoreboard objectives add sts_extra_claims dummy
scoreboard objectives add sts_temp dummy
scoreboard objectives add sts_vars dummy
scoreboard players set #nodrehmal? sts_vars 0

# ===============
## Uncomment this only if you're trying to run this without the Drehmal datapack active.
## Note this may cause unexpected bugs to occur. Use for testing purposes only.
tellraw @a "[Stasis claim] Non-Drehmal mode is active"
scoreboard players set #nodrehmal? sts_vars 1
# ===============
execute if score #nodrehmal? sts_vars matches 1 run scoreboard objectives add sts_click minecraft.used:warped_fungus_on_a_stick

tellraw @a "[Stasis claim] Load success"