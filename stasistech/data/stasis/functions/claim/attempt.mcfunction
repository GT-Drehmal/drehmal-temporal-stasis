# Calculate player's claim capacity
scoreboard players operation #playermax sts_temp = #max sts_claims
scoreboard players operation #playermax sts_temp += @s sts_extra_claims

scoreboard players set #success sts_temp 0
execute store result score #success sts_temp run openpac-claims claim ~ ~

# Error checking
execute unless score #success sts_temp matches 0 if score @s sts_claims >= #playermax sts_temp run tellraw @s [{"text":"AN ERROR OCCURRED!", "color": "red","bold": true},{"text":" Scoreboard and mod claim counts desync (scoreboard > mod).","color": "gray","bold": false},{"text":" Please send this error message to the GT Drehmaris Discord!", "bold": false,"color": "white"}]
#execute if score #success sts_temp matches 0 if score @s sts_claims < #playermax sts_temp run tellraw @s [{"text":"AN ERROR OCCURRED!", "color": "red","bold": true},{"text":" Scoreboard and mod claim counts desync (mod > scoreboard).","color": "gray","bold": false},{"text":" Please send this error message to the GT Drehmaris Discord!", "bold": false,"color": "white"}] 
execute if score @s sts_claims matches ..-1 run tellraw @s [{"text":"AN ERROR OCCURRED!", "color": "red","bold": true},{"text":" Number of claims cannot be negative (found ", "color": "gray","bold": false},{"score":{"name":"@s","objective":"sts_claims"}},{"text":"). Please send this error message to the GT Drehmaris Discord!", "bold": false,"color": "white"}]

# Feedback
execute if score @s sts_claims > #playermax sts_temp run say Too many claimed chunks
execute if score @s sts_claims = #playermax sts_temp run say Claim Capacity Full
execute unless score @s sts_claims >= #playermax sts_temp if score #success sts_temp matches 0 run say claim fail!
execute unless score #success sts_temp matches 0 at @s run function stasis:claim/success

# FX
# Success case (and scoreboard manipulation) handled by stasis:claim/success
# Do not need to check sts_claims because openpac-claims claim would have failed regardless
execute if score #success sts_temp matches 0 at @s run function stasis:playsound/fail
execute if score #success sts_temp matches 0 at @s run function stasis:particles/fail