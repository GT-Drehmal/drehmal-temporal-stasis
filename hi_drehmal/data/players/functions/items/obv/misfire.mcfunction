execute as @e[type=item,tag=!scanned,predicate=players:is_oblivion] run function players:items/obv/give_back
item replace entity @s weapon.mainhand from block 1000000 0 1000000 container.0
setblock 1000000 0 1000000 air
scoreboard players operation #secs temp = @s obv_cool
scoreboard players add #secs temp 19
scoreboard players operation #secs temp /= #20 const
playsound minecraft:dcustom.block.anvil.land player @s ~ ~ ~ 0.5 2
tellraw @s ["",{"text":"Force of Nothing is on cooldown for ","color":"red"},{"score":{"name":"#secs","objective":"temp"},"color":"red"},{"text":"s","color":"red"}]
