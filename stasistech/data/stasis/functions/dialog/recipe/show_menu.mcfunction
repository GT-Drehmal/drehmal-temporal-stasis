scoreboard players reset @s sts_tg_menu
scoreboard players enable @s sts_tg_menu
execute at @s run function stasis:playsound/avsys_msg

tellraw @s ["[",{"text":"ａｖＳＹＳ","color":"aqua"},"] －－－－－－－－－－－－－－－－－－－－－－"]
tellraw @s [{"text":"["},{"text":"ａｖＳＹＳ","color":"aqua"},{"text":"] "}]
tellraw @s [{"text":"["},{"text":"ａｖＳＹＳ","color":"aqua"},{"text":"] "}, {"text": "ＲＥＭＯＴＥ　ＣＯＭＭＡＮＤ　ＩＮＴＥＲＦＡＣＥ","color": "white"}]
tellraw @s [{"text":"["},{"text":"ａｖＳＹＳ","color":"aqua"},{"text":"] "}]
tellraw @s [{"text":"["},{"text":"ａｖＳＹＳ","color":"aqua"},{"text":"] "}, {"text": "ＲＥＣＩＰＥＳ", "color":"white"}]
tellraw @s [{"text":"["},{"text":"ａｖＳＹＳ","color":"aqua"},{"text":"] "}, {"text":"    ［"},{"text":"ＲＵＮＩＣ　ＨＯＵＲＧＬＡＳＳ","color":"aqua","underlined":true,"hoverEvent":{"action":"show_text","value":[{"text":"/trigger sts_tg_get_recipe_hourglass"}]},"clickEvent":{"action":"run_command","value":"/trigger sts_tg_get_recipe_hourglass"}},{"text":"］"}]
tellraw @s [{"text":"["},{"text":"ａｖＳＹＳ","color":"aqua"},{"text":"] "}, {"text":"    ［"},{"text":"ＴＩＤＥＳ　ＩＮ　Ａ　ＢＵＢＢＬＥ","color":"aqua","underlined":true,"hoverEvent":{"action":"show_text","value":[{"text":"/trigger sts_tg_get_recipe_bubble"}]},"clickEvent":{"action":"run_command","value":"/trigger sts_tg_get_recipe_bubble"}},{"text":"］"}]
tellraw @s [{"text":"["},{"text":"ａｖＳＹＳ","color":"aqua"},{"text":"] "}, {"text": "ＭＩＳＣＥＬＬＡＮＥＯＵＳ", "color":"white"}]
tellraw @s [{"text":"["},{"text":"ａｖＳＹＳ","color":"aqua"},{"text":"] "}, {"text":"    ［"},{"text":"ＲＥＭＡＩＮＩＮＧ　ＣＬＡＩＭＳ","color":"aqua","underlined":true,"hoverEvent":{"action":"show_text","value":[{"text":"/trigger sts_tg_get_remaining"}]},"clickEvent":{"action":"run_command","value":"/trigger sts_tg_get_remaining"}},{"text":"］     ［"},{"text":"ＭＥＮＵ","color":"aqua","underlined":true,"hoverEvent":{"action":"show_text","value":[{"text":"/trigger sts_tg_menu"}]},"clickEvent":{"action":"run_command","value":"/trigger sts_tg_menu"}},{"text":"］"}]
tellraw @s [{"text":"["},{"text":"ａｖＳＹＳ","color":"aqua"},{"text":"] "}]