## Called at the player's position when a splash potion is thrown
scoreboard players reset @s sts_throw_water
# Find the potion entity
tag @e[distance=0..2,type=minecraft:potion,nbt={Item:{tag:{Potion:"minecraft:mundane"}}}] add sts_crafting_thrown_water