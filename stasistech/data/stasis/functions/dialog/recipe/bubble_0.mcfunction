tag @s add sts_recipe_bubble_dialog
function stasis:dialog/recipe/query
schedule function stasis:dialog/recipe/bubble_1 2s replace
scoreboard players reset @s sts_tg_get_recipe_bubble
scoreboard players enable @s sts_tg_get_recipe_bubble