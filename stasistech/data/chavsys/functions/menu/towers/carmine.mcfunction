execute if score carmine towers matches 1 run tellraw @s [{"text":"  "},{"text":"●","color":"red"},{"text":"  ","color":"white","underlined":false},{"text":"ＣＡＲＭＩＮＥ","color":"red","underlined":true,"hoverEvent":{"action":"show_text","value":[{"text":"Click to teleport"}]},"clickEvent":{"action":"run_command","value":"/trigger chavsys_carmine"}}]
execute unless score carmine towers matches 1 run tellraw @s [{"text":"  "},{"text":"○","color":"dark_red"},{"text":"  ","color":"white","strikethrough":false},{"text":"ＣＡＲＭＩＮＥ","color":"dark_red","strikethrough":true}]
tellraw @s ""
