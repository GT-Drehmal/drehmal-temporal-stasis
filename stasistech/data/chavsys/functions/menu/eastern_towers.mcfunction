tellraw @s ""
tellraw @s [{"text":"= ＋ = ＋ = ＋ =","color":"white","bold":false},{"text":" ＥＡＳＴＥＲＮ　ＴＯＷＥＲＳ ","color":"blue","bold":true},{"text":"= ＋ = ＋ = ＋ ="}]
# tellraw @s {"text": "          Eastern Towers", "color": "blue", "underlined": true}
tellraw @s ""

function chavsys:menu/towers/black_jungle
function chavsys:menu/towers/purity_peaks
function chavsys:menu/towers/heartwood
function chavsys:menu/towers/maels_desolation
function chavsys:menu/towers/highfall_tundra
function chavsys:menu/towers/akhlo_rohma
function chavsys:menu/towers/grand_pike_canyon
function chavsys:menu/towers/spearhead_forest
function chavsys:menu/towers/veruhkt_plateau
function chavsys:menu/towers/frozen_bite
function chavsys:menu/towers/faehrcyle

tellraw @s [{"text":"[","color":"white","underlined":false},{"text":"ＢＡＣＫ","color":"dark_aqua","underlined":true,"hoverEvent":{"action":"show_text","contents":{"text":"Return to menu"}},"clickEvent":{"action":"run_command","value":"/trigger chavsys_menu"}},{"text":"]"}]
tellraw @s ""
