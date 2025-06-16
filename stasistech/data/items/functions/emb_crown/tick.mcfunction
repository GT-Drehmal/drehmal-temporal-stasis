execute as @a[predicate=items:wearing_embered_crown] unless score @s embc_deaths matches 1.. run function items:emb_crown/set_on_fire
execute as @a[predicate=items:wearing_embered_crown] if score @s embc_deaths matches 1.. run function items:emb_crown/return_to_inv
