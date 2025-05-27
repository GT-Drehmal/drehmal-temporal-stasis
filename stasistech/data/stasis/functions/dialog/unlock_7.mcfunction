tellraw @a[tag=sts_initial_hourglass_dialog_7] [{"text":"["},{"text":"ａｖＳＹＳ","color":"aqua"},{"text":"] "},{"text":"／／"},{"text":"ＮＥＸＴ　ＳＴＥＰ：　ＥＭＰＬＯＹ　ＥＭＥＲＧＥＮＣＹ　ＭＥＣＨＡＮＩＳＭ　"},{"text":"ＳＥＣＴＩＯＮ　２９　ＩＴＥＭ　１４　＂ＲＵＮＩＣ　ＨＯＵＲＧＬＡＳＳ＂","color":"dark_aqua","underlined":true,"hoverEvent":{"action":"show_text","value":[{"text":"Click to view recipe"}]},"clickEvent":{"action":"run_command","value":"/trigger sts_tg_get_recipe_hourglass"}},{"text":"　ＴＯ　ＭＩＮＩＭＩＺＥ　ＤＡＭＡＧＥ．"},{"text":"／／"}]
execute as @a[tag=sts_initial_hourglass_dialog_7] at @s run function stasis:playsound/avsys_task
tag @a[tag=sts_initial_hourglass_dialog_7] add sts_initial_hourglass_dialog_check
tag @a[tag=sts_initial_hourglass_dialog_7] remove sts_initial_hourglass_dialog_7
schedule function stasis:dialog/unlock_check_give 4s append