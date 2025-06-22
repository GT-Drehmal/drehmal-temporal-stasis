execute if score av_sal towers matches 1 run tellraw @s [{"text":"  "},{"text":"●","color":"green"},{"text":"  ","color":"white","underlined":false},{"text":"ＡＶ＇ＳＡＬ","color":"green","underlined":true,"hoverEvent":{"action":"show_text","value":[{"text":"Click to teleport"}]},"clickEvent":{"action":"run_command","value":"/trigger chavsys_av_sal"}}]
execute unless score av_sal towers matches 1 run tellraw @s [{"text":"  "},{"text":"○","color":"dark_green"},{"text":"  ","color":"white","strikethrough":false},{"text":"ＡＶ＇ＳＡＬ","color":"dark_green","strikethrough":true}]
tellraw @s ""
