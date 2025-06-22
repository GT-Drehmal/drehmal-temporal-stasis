execute if score anyr_nogur towers matches 1 run tellraw @s [{"text":"  "},{"text":"●","color":"red"},{"text":"  ","color":"white","underlined":false},{"text":"ＡＮＹＲ＇ＮＯＧＵＲ","color":"red","underlined":true,"hoverEvent":{"action":"show_text","value":[{"text":"Click to teleport"}]},"clickEvent":{"action":"run_command","value":"/trigger chavsys_anyr_nogur"}}]
execute unless score anyr_nogur towers matches 1 run tellraw @s [{"text":"  "},{"text":"○","color":"dark_red"},{"text":"  ","color":"white","strikethrough":false},{"text":"ＡＮＹＲ＇ＮＯＧＵＲ","color":"dark_red","strikethrough":true}]
tellraw @s ""
