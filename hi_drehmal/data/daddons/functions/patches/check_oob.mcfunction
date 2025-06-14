## Warns and then fucking kills a player if they are out of bounds. I.e. detected to be outside play area and not in one of the valid locations (e.g. the terminus)
# Predicate is also responsible for checking if player is dev or has already been killed
# Predicate doesn't check game mode because strange bug. 
execute as @a[predicate=daddons:out_of_bounds,gamemode=!spectator,gamemode=!creative] run function daddons:patches/out_of_bounds
execute as @a[predicate=!daddons:out_of_bounds,scores={oob_warning=0..}] run scoreboard players reset @s oob_warning
# Player has respawned / didn't die (??)
execute as @a[scores={player_hp=1..,oob_murdered=1}] run scoreboard players reset @s oob_murdered