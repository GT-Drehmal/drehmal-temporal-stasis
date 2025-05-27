tellraw @a[tag=sts_initial_hourglass_dialog_6] [{"text":"["},{"text":"ａｖＳＹＳ","color":"aqua"},{"text":"] "},{"text":"／／"},{"text":"ＲＥＣＯＶＥＲＹ：　"},{"text":"ＩＭＰＲＯＢＡＢＬＥ","color":"red"},{"text":"．／／"}]
execute as @a[tag=sts_initial_hourglass_dialog_6] at @s run function stasis:playsound/avsys_msg
tag @a[tag=sts_initial_hourglass_dialog_6] add sts_initial_hourglass_dialog_7
tag @a[tag=sts_initial_hourglass_dialog_6] remove sts_initial_hourglass_dialog_6
schedule function stasis:dialog/unlock_7 4s append
