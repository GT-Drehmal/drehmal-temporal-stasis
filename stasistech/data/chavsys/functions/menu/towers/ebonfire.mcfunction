execute if score ebonfire towers matches 1 run tellraw @s [{"text":"  "},{"text":"●","color":"red"},{"text":"  ","color":"white","underlined":false},{"text":"ＥＢＯＮＦＩＲＥ","color":"red","underlined":true,"hoverEvent":{"action":"show_text","value":[{"text":"Click to teleport"}]},"clickEvent":{"action":"run_command","value":"/trigger chavsys_ebonfire"}}]
execute unless score ebonfire towers matches 1 run tellraw @s [{"text":"  "},{"text":"○","color":"dark_red"},{"text":"  ","color":"white","strikethrough":false},{"text":"ＥＢＯＮＦＩＲＥ","color":"dark_red","strikethrough":true}]
tellraw @s ""
