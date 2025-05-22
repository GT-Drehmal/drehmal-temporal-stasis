scoreboard objectives remove sts_claims
scoreboard objectives remove sts_extra_claims
scoreboard objectives remove sts_bool_received_hourglass
scoreboard objectives remove sts_tg_get_remaining
scoreboard objectives remove sts_tg_get_recipe_hourglass
scoreboard objectives remove sts_tg_get_recipe_bubble
scoreboard objectives remove sts_click
scoreboard objectives remove sts_use_pearl
scoreboard objectives remove sts_throw_potion
scoreboard players reset #success sts_temp
scoreboard players reset #nodrehmal? sts_vars
function stasis:lock
function stasis:load

tellraw @s [{"text":"IMPORTANT! ","color":"yellow","bold":true},{"text":"You have reset the datapack part of Stasis chunk claims, ","color":"gray","bold": false},{"text":"but this doesn't reset actual claim data! ","color":"white","bold": false}, {"text":"You must also delete both ","color":"gray","bold": false},{"text":"player-claims/","color":"gray","italic": true,"bold": false},{"text": " and ","color": "gray", "italic": false,"bold": false},{"text": "parties/","color": "gray","italic": true,"bold": false},{"text": " in ","color": "gray","italic": false,"bold": false},{"text": "<world>/data/openpartiesandclaims/","color": "gray","italic": true,"bold": false},{"text":", or desync could happen!","color":"gray","italic": false,"bold": false}]
