execute if score faehrcyle towers matches 1 run tellraw @s [{"text":"  "},{"text":"●","color":"blue"},{"text":"  ","color":"white","underlined":false},{"text":"ＦＡＥＨＲＣＹＬＥ","color":"blue","underlined":true,"hoverEvent":{"action":"show_text","value":[{"text":"Click to teleport"}]},"clickEvent":{"action":"run_command","value":"/trigger chavsys_faehrcyle"}}]
execute unless score faehrcyle towers matches 1 run tellraw @s [{"text":"  "},{"text":"○","color":"dark_blue"},{"text":"  ","color":"white","strikethrough":false},{"text":"ＦＡＥＨＲＣＹＬＥ","color":"dark_blue","strikethrough":true}]
tellraw @s ""
