execute if score sahd towers matches 1 run tellraw @s [{"text":"  "},{"text":"●","color":"yellow"},{"text":"  ","color":"white","underlined":false},{"text":"ＳＡＨＤ","color":"yellow","underlined":true,"hoverEvent":{"action":"show_text","value":[{"text":"Click to teleport"}]},"clickEvent":{"action":"run_command","value":"/trigger chavsys_sahd"}}]
execute unless score sahd towers matches 1 run tellraw @s [{"text":"  "},{"text":"○","color":"dark_gray"},{"text":"  ","color":"white","strikethrough":false},{"text":"ＳＡＨＤ","color":"dark_gray","strikethrough":true}]
tellraw @s ""
