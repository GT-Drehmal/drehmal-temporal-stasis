## Execute as player wearing the crown
execute unless predicate items:player/wearing_modified_embered_crown run function items:emb_crown/modify_wearing
execute unless score @s embc_deaths matches 1.. unless predicate players:adventure_areas as @s run summon small_fireball ~ ~2.1 ~ {Silent:1b,HasVisualFire:0b,power:[0.0,-2.2,0.0],Tags:["embc_fire"],Item:{id:"minecraft:air",Count:1}}
execute unless score @s embc_deaths matches 1.. unless predicate items:player/has_fire_res run effect give @s minecraft:regeneration 2 2 true
# Failsafe
execute unless score @s embc_deaths matches 1.. unless predicate items:player/on_fire if score #5T timer matches 0 run damage @s 5 minecraft:on_fire
# Reset after death
execute if score @s embc_deaths matches 1.. as @e[type=minecraft:small_fireball,tag=embc_fire] run kill @s
execute if score @s embc_deaths matches 1.. run function items:emb_crown/return_to_inv