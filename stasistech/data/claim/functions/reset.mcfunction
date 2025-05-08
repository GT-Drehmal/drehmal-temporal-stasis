scoreboard objectives remove sts_claims
scoreboard objectives remove sts_extra_claims
scoreboard players reset #success sts_temp
scoreboard players reset #nodrehmal? sts_vars

tellraw @s [{"text":"IMPORTANT! ","color":"yellow","bold":true},{"text":"You have reset the datapack part of Stasis chunk claims, ","color":"gray","bold": false},{"text":"but this doesn't reset actual claim data! ","color":"white","bold": false}]
tellraw @s [{"text":"You must also delete both ","color":"white","bold": false},{"text":"player-claims/","color":"gray","italic": true,"bold": false},{"text": " and ","color": "gray", "italic": false,"bold": false},{"text": "parties/","color": "gray","italic": true,"bold": false},{"text": " in ","color": "gray","italic": false,"bold": false},{"text": "<world>/data/openpartiesandclaims/","color": "gray","italic": true,"bold": false},{"text":", or desync could happen!","color":"white","italic": false,"bold": false}]
