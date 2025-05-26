## Scoreboard resets are handled by each function
# Item usage
execute if score #enabled sts_vars matches 1 as @a if score @s sts_click matches 1.. run function stasis:click
execute if score #enabled sts_vars matches 1 as @a if score @s sts_throw_potion matches 1.. at @s run function stasis:crafting/tides_in_a_bubble/check_splash_potion
execute if score #enabled sts_vars matches 1 as @e[type=minecraft:potion, tag=sts_crafting_thrown_mundane] at @s run function stasis:crafting/tides_in_a_bubble/check_items
execute if score #enabled sts_vars matches 1 as @a if score @s sts_use_pearl matches 1.. at @s run function stasis:crafting/runic_hourglass/check_pearl
execute if score #enabled sts_vars matches 1 as @e[type=minecraft:ender_pearl, tag=sts_crafting_thrown_pearl] at @s run function stasis:crafting/runic_hourglass/check_items
execute unless score #enabled sts_vars matches 1 run scoreboard players reset @a sts_click

## Triggers
execute if score #enabled sts_vars matches 1 run function stasis:enable_triggers
execute if score #enabled sts_vars matches 1 as @a if score @s sts_tg_get_remaining matches 1.. run function stasis:dialog/get_remaining
execute if score #enabled sts_vars matches 1 as @a if score @s sts_tg_get_recipe_hourglass matches 1.. run function stasis:dialog/recipe/hourglass_0
execute if score #enabled sts_vars matches 1 as @a if score @s sts_tg_get_recipe_bubble matches 1.. run function stasis:dialog/recipe/bubble_0

## Testing zone
# execute as @e[tag=sts_crafting_thrown_mundane] run say aaaa