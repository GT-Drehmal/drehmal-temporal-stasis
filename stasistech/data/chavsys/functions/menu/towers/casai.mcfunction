execute if score casai towers matches 1 run tellraw @s [{"text":"  "},{"text":"●","color":"red"},{"text":"  ","color":"white","underlined":false},{"text":"ＣＡＳＡＩ","color":"red","underlined":true,"hoverEvent":{"action":"show_text","value":[{"text":"Click to teleport"}]},"clickEvent":{"action":"run_command","value":"/trigger chavsys_casai"}}]
execute unless score casai towers matches 1 run tellraw @s [{"text":"  "},{"text":"○","color":"dark_red"},{"text":"  ","color":"white","strikethrough":false},{"text":"ＣＡＳＡＩ","color":"dark_red","strikethrough":true}]
tellraw @s ""
