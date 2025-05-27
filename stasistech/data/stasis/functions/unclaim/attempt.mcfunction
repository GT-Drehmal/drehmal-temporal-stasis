scoreboard players set #success sts_temp 0
execute store result score #success sts_temp run openpac-claims unclaim ~ ~

# Error Checking
execute unless score #success sts_temp matches 0 if score @s sts_claims matches 0 run tellraw @s [{"text":"AN ERROR OCCURRED!", "color": "red","bold": true},{"text":" Scoreboard and mod claim counts desync (mod > scoreboard).","color": "gray","bold": false},{"text":" Please send this error message to the GT Drehmaris Discord!", "bold": false,"color": "white"}]
execute if score @s sts_claims matches ..-1 run tellraw @s [{"text":"AN ERROR OCCURRED!", "color": "red","bold": true},{"text":" Number of claims cannot be negative (found ", "color": "gray","bold": false},{"score":{"name":"@s","objective":"sts_claims"}},{"text":"). Please send this error message to the GT Drehmaris Discord!", "bold": false,"color": "white"}]

# Feedback
execute if score @s sts_claims matches 0 run tellraw @s [{"text":"You don't have any chunks to unclaim!", "color": "red"}]
execute unless score @s sts_claims matches 0 if score #success sts_temp matches 0 run tellraw @s [{"text": "This chunk does not belong to you.", "color": "gray"}]
execute unless score #success sts_temp matches 0 at @s run function stasis:unclaim/success

# FX
# Success case (and scoreboard manipulation) handled by stasis:unclaim/success
execute if score #success sts_temp matches 0 at @s run function stasis:playsound/fail
execute if score #success sts_temp matches 0 at @s run function stasis:particles/fail