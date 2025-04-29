execute as @e[type=item,tag=!scanned,predicate=players:is_asc] run function players:items/asc/give_back
execute if predicate players:holding/empty run item replace entity @s weapon.mainhand from block 1000000 14 1000000 container.0
execute unless predicate players:holding/empty run tag @s add asc_cd
execute if predicate players:holding/asc run setblock 1000000 14 1000000 air
scoreboard players operation #secs temp = @s asc_cool
scoreboard players add #secs temp 19
scoreboard players operation #secs temp /= #20 const
playsound minecraft:dcustom.block.anvil.land player @s ~ ~ ~ 0.5 2
tellraw @s ["",{"text":"Holy Moonlight is on cooldown for ","color":"red"},{"score":{"name":"#secs","objective":"temp"},"color":"red"},{"text":"s","color":"red"}]
execute if predicate players:holding/asc run tag @s remove asc_cd
