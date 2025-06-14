# Run as the player who is confirmed out of bounds
scoreboard players add @s oob_warning 0
execute if score @s oob_warning matches 0 run tellraw @s [{"text":"YOU ARE OUT OF BOUNDS! ","color":"dark_red","bold":true},{"text":"You have","color":"white","bold":false},{"text":" 3 ","color":"yellow"},{"text":"seconds to go back in bounds before you are killed.","color":"white","bold":false}]
execute if score @s oob_warning matches 20 run tellraw @s [{"text":"YOU ARE OUT OF BOUNDS! ","color":"dark_red","bold":true},{"text":"You have","color":"white","bold":false},{"text":" 2 ","color":"gold"},{"text":"seconds to go back in bounds before you are killed.","color":"white","bold":false}]
execute if score @s oob_warning matches 40 run tellraw @s [{"text":"YOU ARE OUT OF BOUNDS! ","color":"dark_red","bold":true},{"text":"You have","color":"white","bold":false},{"text":" 1 ","color":"red"},{"text":"more second to go back in bounds before you are killed.","color":"white","bold":false}]
execute unless score @s oob_warning matches 60.. run scoreboard players add @s oob_warning 1
execute if score @s oob_warning matches 60.. run function players:spawn/default_spawn
execute if score @s oob_warning matches 60.. run damage @s 8192 minecraft:idk
execute if score @s oob_warning matches 60.. run scoreboard players set @s oob_murdered 1
execute if score @s oob_warning matches 60.. run scoreboard players reset @s oob_warning