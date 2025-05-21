scoreboard players set @s sts_bool_received_hourglass 1
playsound minecraft:block.beacon.ambient master @s ~ ~ ~ 1 1.38
tellraw @s {"text":"A wave of runic energy rushes over you...","color":"light_purple","italic":true}
tag @s add sts_initial_hourglass_dialog
schedule function stasis:dialog/unlock_1 4s append