execute if score @s wasHoldingSy matches 0 run title @s actionbar ["",{"text":"Weapon State: ","color":"dark_aqua"},{"text":"Running","color":"yellow"}]
execute if score @s wasHoldingSy matches 0 run scoreboard players reset @s sy_minicool
execute unless entity @s[tag=syzygy_crawl] run scoreboard players add @s sy_minicool 1
execute unless entity @s[tag=syzygy_crawl] if score @s sy_cool matches 1.. if score @s sy_minicool matches 15.. run function players:items/syzygy/cooldown