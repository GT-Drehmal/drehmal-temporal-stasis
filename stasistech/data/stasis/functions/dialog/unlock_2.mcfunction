tellraw @a[tag=sts_initial_hourglass_dialog_2] [{"text":"["},{"text":"ａｖＳＹＳ","color":"aqua"},{"text":"] "},{"text":"／／"},{"text":"ＡＮＡＬＹＺＩＮＧ．．．"},{"text":"／／"}]
tag @a[tag=sts_initial_hourglass_dialog_2] add sts_initial_hourglass_dialog_3
tag @a[tag=sts_initial_hourglass_dialog_2] remove sts_initial_hourglass_dialog_2
schedule function stasis:dialog/unlock_3 4s append