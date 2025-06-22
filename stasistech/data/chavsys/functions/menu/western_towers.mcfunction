tellraw @s ""
tellraw @s [{"text":"= ＋ = ＋ = ＋ =","color":"white","bold":false},{"text":" ＷＥＳＴＥＲＮ　ＴＯＷＥＲＳ ","color":"red","bold":true},{"text":"= ＋ = ＋ = ＋ ="}]
# tellraw @s {"text": "          Western Towers", "color": "red", "underlined": true}
tellraw @s ""

function chavsys:menu/towers/anyr_nogur
function chavsys:menu/towers/carmine
function chavsys:menu/towers/casai
function chavsys:menu/towers/ebonfire
function chavsys:menu/towers/ebony_veldt
function chavsys:menu/towers/lorahn_kahl
function chavsys:menu/towers/merijool
function chavsys:menu/towers/nimahj_swamp
function chavsys:menu/towers/north_tharxax
function chavsys:menu/towers/south_tharxax
function chavsys:menu/towers/hellcrags

tellraw @s [{"text":"[","color":"white","underlined":false},{"text":"ＢＡＣＫ","color":"dark_aqua","underlined":true,"hoverEvent":{"action":"show_text","contents":{"text":"Return to menu"}},"clickEvent":{"action":"run_command","value":"/trigger chavsys_menu"}},{"text":"]"}]
tellraw @s ""
