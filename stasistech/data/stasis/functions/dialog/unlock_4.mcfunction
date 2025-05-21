tellraw @a[tag=sts_initial_hourglass_dialog_4] [{"text":"["},{"text":"ａｖＳＹＳ","color":"aqua"},{"text":"] "},{"text":"／／"},{"text":"ＩＭＰＡＣＴ：　ＴＥＭＰＯＲＡＬ　ＡＮＯＭＡＬＹ"},{"text":"／／"}]
tag @a[tag=sts_initial_hourglass_dialog_4] add sts_initial_hourglass_dialog_5
tag @a[tag=sts_initial_hourglass_dialog_4] remove sts_initial_hourglass_dialog_4
schedule function stasis:dialog/unlock_5 4s append
