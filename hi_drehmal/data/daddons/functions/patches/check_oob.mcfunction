## Warns and then fucking kills a player if they are out of bounds. I.e. detected to be outside play area and not in one of the valid locations (e.g. the terminus)
execute as @a[predicate=daddons:out_of_bounds] run function daddons:patches/out_of_bounds
execute as @a[predicate=!daddons:out_of_bounds,scores={oob_warning=0..}] run scoreboard players reset @s oob_warning
