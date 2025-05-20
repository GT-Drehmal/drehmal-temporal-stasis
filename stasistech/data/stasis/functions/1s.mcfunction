schedule function stasis:1s 1s replace

execute if score #enabled sts_vars matches 1 as @a unless score @s sts_received_hourglass matches 0 run function stasis:give/runic_hourglass