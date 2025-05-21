## Scoreboard resets are handled by each function
# Item usage
execute if score #enabled sts_vars matches 1 as @a if score @s sts_click matches 1.. run function stasis:click

## Triggers
execute if score #enabled sts_vars matches 1 run function stasis:enable_triggers
execute if score #enabled sts_vars matches 1 as @a if score @s sts_tg_get_remaining matches 1.. run function stasis:dialog/get_remaining
execute if score #enabled sts_vars matches 1 as @a if score @s sts_tg_get_recipe_hourglass matches 1.. run function stasis:dialog/recipe/hourglass_0
execute if score #enabled sts_vars matches 1 as @a if score @s sts_tg_get_recipe_bubble matches 1.. run function stasis:dialog/recipe/bubble_0