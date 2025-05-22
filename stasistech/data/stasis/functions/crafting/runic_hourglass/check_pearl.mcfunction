## Called at the player's position when a pearl is used
scoreboard players reset @s sts_use_pearl
# Find the potion entity
tag @e[distance=0..2,type=minecraft:ender_pearl] add sts_crafting_thrown_pearl