tellraw @s ""
tellraw @s [{"text":"= ＋ = ＋ = ＋ =","color":"white","bold":false},{"text":" ＯＵＴＥＲ　ＴＯＷＥＲＳ ","color":"yellow","bold":true},{"text":"= ＋ = ＋ = ＋ ="}]
# tellraw @s {"text": "          Outer Towers", "color": "yellow", "underlined": true}
tellraw @s ""

function chavsys:menu/towers/sahd
function chavsys:menu/towers/dawn_island
function chavsys:menu/towers/dusk_island
function chavsys:menu/towers/aphelion
function chavsys:menu/towers/lo_dahr
function chavsys:menu/towers/yavhlix

tellraw @s [{"text":"[","color":"white","underlined":false},{"text":"ＢＡＣＫ","color":"dark_aqua","underlined":true,"hoverEvent":{"action":"show_text","contents":{"text":"Return to menu"}},"clickEvent":{"action":"run_command","value":"/trigger chavsys_menu"}},{"text":"]"}]
tellraw @s ""
