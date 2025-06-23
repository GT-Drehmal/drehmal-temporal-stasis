function stasis:enable_triggers
function stasis:playsound/runic_energy
tellraw @s {"text":"A wave of runic energy rushes over you...","color":"light_purple","italic":true}
tag @s add sts_initial_hourglass_dialog
scoreboard players set @s sts_bool_seen_unlock_dialog 1
schedule function stasis:dialog/unlock_1 4s append