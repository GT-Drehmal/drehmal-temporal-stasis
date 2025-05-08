# Calculate player's claim capacity
scoreboard players operation #playermax sts_temp = #max sts_claims
scoreboard players operation #playermax sts_temp += @s sts_extra_claims

scoreboard players set #success sts_temp 0
execute store result score #success sts_temp run openpac-claims claim ~ ~

execute if score @s sts_claims > #playermax sts_temp run say Too many claimed chunks
execute if score @s sts_claims = #playermax sts_temp run say Claim Capacity Full
execute unless score @s sts_claims >= #playermax sts_temp if score #success sts_temp matches 0 run function claim:fail
execute unless score #success sts_temp matches 0 run function claim:success
execute if score @s sts_claims >= #playermax sts_temp unless score #success sts_temp matches 0 run tellraw @s [{"text":"[AN ERROR OCCURRED!]", "color": "red","bold": true},{"text":" Scoreboard and mod claim counts desync (scoreboard > mod).","color": "gray","bold": false},{"text":" Please send this error message to the Drehmaris Discord!", "bold": false,"color": "white"}]