tag @s add sts_recipe_hourglass_dialog
function stasis:dialog/recipe/query
schedule function stasis:dialog/recipe/hourglass_1 4s append
scoreboard players reset @s sts_tg_get_recipe_hourglass
scoreboard players enable @s sts_tg_get_recipe_hourglass