execute unless entity @s[tag=owner_tagged] run function entities:misc/epearl_owner
## Forced progression: Only checks EP if story enabled and tower reaches 25%
execute unless score #story_disabled? bool matches 1 if score count_all towers matches 8.. if entity @s[predicate=players:overworld,x=2416.5,y=144.0,z=1177.5,dx=2,dy=3,dz=2] run function entities:misc/epearl_tp_player
execute unless entity @s[tag=nofizzle] if entity @s[predicate=players:true_end] run function entities:misc/fizzle_condition
