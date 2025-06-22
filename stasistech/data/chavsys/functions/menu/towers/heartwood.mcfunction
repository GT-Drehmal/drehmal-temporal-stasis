execute if score heartwood towers matches 1 run tellraw @s [{"text":"  "},{"text":"●","color":"blue"},{"text":"  ","color":"white","underlined":false},{"text":"ＨＥＡＲＴＷＯＯＤ","color":"blue","underlined":true,"hoverEvent":{"action":"show_text","value":[{"text":"Click to teleport"}]},"clickEvent":{"action":"run_command","value":"/trigger chavsys_heartwood"}}]
execute unless score heartwood towers matches 1 run tellraw @s [{"text":"  "},{"text":"○","color":"dark_blue"},{"text":"  ","color":"white","strikethrough":false},{"text":"ＨＥＡＲＴＷＯＯＤ","color":"dark_blue","strikethrough":true}]
tellraw @s ""
