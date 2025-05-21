tellraw @a[tag=sts_initial_hourglass_dialog] [{"text":"["},{"text":"ａｖＳＹＳ","color":"aqua"},{"text":"] "},{"text":"／／"},{"text":"ＷＡＲＮＩＮＧ：　ＡＮＯＭＡＬＯＵＳ　ＳＴＡＴＥ　ＤＥＴＥＣＴＥＤ　ＩＮ　ＴＥＭＰＯＲＡＬ　ＥＮＧＩＮＥ"},{"text":"／／"}]
tag @a[tag=sts_initial_hourglass_dialog] add sts_initial_hourglass_dialog_2
tag @a[tag=sts_initial_hourglass_dialog] remove sts_initial_hourglass_dialog
schedule function stasis:dialog/unlock_2 4s append