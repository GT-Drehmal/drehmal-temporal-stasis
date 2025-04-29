scoreboard players operation #secs temp = @s cal_cool
scoreboard players add #secs temp 19
scoreboard players operation #secs temp /= #20 const

execute if score @s cal_cool matches 2.. if score #secs temp matches 20.. run title @s actionbar ["",{"text":"True Catastrophe Cooldown: ","color":"gray"},{"score":{"name":"#secs","objective":"temp"},"color":"red"},{"text":"s","color":"red"}]
execute if score @s cal_cool matches 2.. if score #secs temp matches 6..19 run title @s actionbar ["",{"text":"True Catastrophe Cooldown: ","color":"gray"},{"score":{"name":"#secs","objective":"temp"},"color":"yellow"},{"text":"s","color":"yellow"}]
execute if score @s cal_cool matches 2.. if score #secs temp matches ..5 run title @s actionbar ["",{"text":"True Catastrophe Cooldown: ","color":"gray"},{"score":{"name":"#secs","objective":"temp"},"color":"green"},{"text":"s","color":"green"}]
execute unless score @s cal_cool matches 2.. run title @s actionbar {"text":"True Catastrophe is ready for use","color":"green"}
