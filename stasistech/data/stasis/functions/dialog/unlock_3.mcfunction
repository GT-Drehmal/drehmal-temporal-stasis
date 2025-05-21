tellraw @a[tag=sts_initial_hourglass_dialog_3] [{"text":"["},{"text":"ａｖＳＹＳ","color":"aqua"},{"text":"] "},{"text":"／／"},{"text":"ＥＲＲＯＲ：　ＵＮＫＮＯＷＮ　ＢＯＵＮＤＳ"},{"text":"／／"}]
tag @a[tag=sts_initial_hourglass_dialog_3] add sts_initial_hourglass_dialog_4
tag @a[tag=sts_initial_hourglass_dialog_3] remove sts_initial_hourglass_dialog_3
schedule function stasis:dialog/unlock_4 4s append
