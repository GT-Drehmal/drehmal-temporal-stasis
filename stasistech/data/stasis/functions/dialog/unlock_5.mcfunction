tellraw @a[tag=sts_initial_hourglass_dialog_5] [{"text":"["},{"text":"ａｖＳＹＳ","color":"aqua"},{"text":"] "},{"text":"／／"},{"text":"ＳＣＯＰＥ：　ＡＬＬ　ＬＯＣＡＴＩＯＮＳ"},{"text":"／／"}]
execute as @a[tag=sts_initial_hourglass_dialog_5] at @s run function stasis:playsound/avsys_msg
tag @a[tag=sts_initial_hourglass_dialog_5] add sts_initial_hourglass_dialog_6
tag @a[tag=sts_initial_hourglass_dialog_5] remove sts_initial_hourglass_dialog_5
schedule function stasis:dialog/unlock_6 4s append