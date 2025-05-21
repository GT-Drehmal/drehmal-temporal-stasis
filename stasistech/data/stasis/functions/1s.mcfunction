schedule function stasis:1s 1s replace

execute if score #enabled sts_vars matches 1 as @a unless score @s sts_bool_received_hourglass matches 1.. run function stasis:give/initial_hourglass