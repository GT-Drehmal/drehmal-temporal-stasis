tellraw @s ""
tellraw @s [{"text":"= ＋ = ＋ = ＋ =","color":"white","bold":false},{"text":" ＣＥＮＴＲＡＬ　ＴＯＷＥＲＳ ","color":"green","bold":true},{"text":"= ＋ = ＋ = ＋ ="}]
tellraw @s ""

# tellraw @s {"text": "          Central Towers", "color": "green", "underlined": true}
function chavsys:menu/towers/av_sal
function chavsys:menu/towers/capital_valley
function chavsys:menu/towers/gulf_of_drehmal
function chavsys:menu/towers/palisades_heath

tellraw @s [{"text":"[","color":"white","underlined":false},{"text":"ＢＡＣＫ","color":"dark_aqua","underlined":true,"hoverEvent":{"action":"show_text","contents":{"text":"Return to menu"}},"clickEvent":{"action":"run_command","value":"/trigger chavsys_menu"}},{"text":"]"}]
tellraw @s ""
