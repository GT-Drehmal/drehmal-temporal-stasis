# Triggers; reset handled by each function
execute as @a if score @s sts_tg_get_remaining matches 1.. run function stasis:get_remaining

# Non-Drehmal Mode exclusive
execute if score #nodrehmal? sts_vars matches 1 as @a if score @s sts_click matches 1.. if predicate stasis:holding/runic_hourglass at @s run function stasis:claim/attempt
execute if score #nodrehmal? sts_vars matches 1 as @a if score @s sts_click matches 1.. if predicate stasis:holding/tides_in_a_bubble at @s run function stasis:unclaim/attempt
execute if score #nodrehmal? sts_vars matches 1 as @a if score @s sts_click matches 1.. run scoreboard players reset @s sts_click
