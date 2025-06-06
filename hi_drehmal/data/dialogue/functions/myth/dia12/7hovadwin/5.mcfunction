

execute as @a at @s run playsound minecraft:dcustom.entity.wither.ambient ambient @s ~ ~ ~ 1 0
tellraw @a ["","[",{"text":"The Mythoclast","color":"gold"},"]",{"text":" Step through the portal.","color":"gold"}," We are nearing the end."]

# Cleanup past emi fight (if any)
execute in minecraft:true_end run kill @e[type=minecraft:zombie,tag=aj.emis]
execute in minecraft:true_end run kill @e[type=#emis:bone_entities,tag=emissary.corpse]
execute in minecraft:true_end run kill @e[type=#emis:bone_entities,tag=aj.emis]


execute unless score #voidportal bool matches 1.. run scoreboard players set #voidportal bool 1
execute in minecraft:overworld positioned 26512 161 -96 run setblock ~14 ~ ~7 minecraft:black_concrete

# this doesn't seem to serve a purpose
scoreboard players set #myth_dia12_7 bool 2

