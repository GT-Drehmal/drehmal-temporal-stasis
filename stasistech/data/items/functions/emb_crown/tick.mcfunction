execute as @a[predicate=items:wearing_embered_crown] run function items:emb_crown/player_tick
execute at @a[predicate=items:wearing_embered_crown] as @e[type=minecraft:small_fireball,tag=embc_fire,distance=0..5] run function items:emb_crown/fireball_tick
