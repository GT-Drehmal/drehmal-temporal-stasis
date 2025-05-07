execute unless score @s sts_claims >= #max sts_claims store result score #success sts_temp run openpac-claims claim ~ ~
execute if score @s sts_claims > #max sts_claims run tellraw @s "Too many claimed chunks"
execute if score @s sts_claims = #max sts_claims run tellraw @s "Claim Capacity Full"
execute unless score @s sts_claims >= #max sts_claims if score #success sts_temp matches 0 run function claim:fail
execute if score #success sts_temp matches 1 run function claim:success