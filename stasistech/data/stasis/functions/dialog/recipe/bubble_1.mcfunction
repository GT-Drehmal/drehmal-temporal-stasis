#tellraw @a[tag=sts_recipe_bubble_dialog] [{"text":"["},{"text":"ａｖＳＹＳ","color":"aqua"},{"text":"] "},{"text":"／／ＲＥＣＩＰＥ　ＳＴＡＲＴ／／"}]
tellraw @a[tag=sts_recipe_bubble_dialog] ["[",{"text":"ａｖＳＹＳ","color":"aqua"},"] －－－－－－－－－－－－－－－－－－－－－－"]
tellraw @a[tag=sts_recipe_bubble_dialog] [{"text":"["},{"text":"ａｖＳＹＳ","color":"aqua"},{"text":"] "}]
tellraw @a[tag=sts_recipe_bubble_dialog] [{"text":"["},{"text":"ａｖＳＹＳ","color":"aqua"},{"text":"] "},{"text":"３０．４ \"ＴＩＤＥＳ　ＩＮ　Ａ　ＢＵＢＢＬＥ\"","color":"white","underlined":true,"hoverEvent":{"action":"show_text","value":[{"text":"/trigger sts_tg_get_recipe_bubble"}]},"clickEvent":{"action":"suggest_command","value":"/trigger sts_tg_get_recipe_bubble"}}]
tellraw @a[tag=sts_recipe_bubble_dialog] [{"text":"["},{"text":"ａｖＳＹＳ","color":"aqua"},{"text":"] "},{"text":"ＰＲＥＰＡＲＥ　ＯＮ　ＦＬＡＴ　ＳＵＲＦＡＣＥ","bold":true}]
tellraw @a[tag=sts_recipe_bubble_dialog] [{"text":"["},{"text":"ａｖＳＹＳ","color":"aqua"},{"text":"] "},{"text":"    ８ｘ","color":"gray"},{"text":"ＧＬＡＳＳ　ＰＡＮＥＳ"}]
tellraw @a[tag=sts_recipe_bubble_dialog] [{"text":"["},{"text":"ａｖＳＹＳ","color":"aqua"},{"text":"] "},{"text":"    ４ｘ","color":"gray"},{"text":"ＯＲＤＥＲＦＬＡＭＥ　ＴＯＲＣＨＥＳ"}]
tellraw @a[tag=sts_recipe_bubble_dialog] [{"text":"["},{"text":"ａｖＳＹＳ","color":"aqua"},{"text":"] "},{"text":"ＡＮＤ"},{"text":"　ＴＨＲＯＷ","bold":true}]
tellraw @a[tag=sts_recipe_bubble_dialog] [{"text":"["},{"text":"ａｖＳＹＳ","color":"aqua"},{"text":"] "},{"text":"    ＳＰＬＡＳＨ　ＭＵＮＤＡＮＥ　ＰＯＴＩＯＮ","color":"white"}]
tellraw @a[tag=sts_recipe_bubble_dialog] [{"text":"["},{"text":"ａｖＳＹＳ","color":"aqua"},{"text":"] "},{"text":"ＡＴ　ＭＡＴＥＲＩＡＬ．","bold":true}]
#tellraw @a[tag=sts_recipe_bubble_dialog] [{"text":"["},{"text":"ａｖＳＹＳ","color":"aqua"},{"text":"] "},{"text":"／／ＲＥＣＩＰＥ　ＥＮＤ／／"}]
tellraw @a[tag=sts_recipe_bubble_dialog] [{"text":"["},{"text":"ａｖＳＹＳ","color":"aqua"},{"text":"] "}]
execute as @a[tag=sts_recipe_bubble_dialog] run function stasis:dialog/recipe/menu_button
tellraw @a[tag=sts_recipe_bubble_dialog] [{"text":"["},{"text":"ａｖＳＹＳ","color":"aqua"},{"text":"] "}]
execute as @a[tag=sts_recipe_bubble_dialog] at @s run function stasis:playsound/avsys_task

tag @a[tag=sts_recipe_bubble_dialog] remove sts_recipe_bubble_dialog