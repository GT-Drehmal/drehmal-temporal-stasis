execute at @s if predicate items:in_block run kill @s
execute if score @s embc_fbage matches 2.. run kill @s
scoreboard players add @s embc_fbage 1