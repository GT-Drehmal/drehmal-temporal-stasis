tag @s add sts_recipe_bubble_dialog
execute at @s run function stasis:dialog/recipe/query
schedule function stasis:dialog/recipe/bubble_1 4s append
scoreboard players reset @s sts_tg_get_recipe_bubble
scoreboard players enable @s sts_tg_get_recipe_bubble