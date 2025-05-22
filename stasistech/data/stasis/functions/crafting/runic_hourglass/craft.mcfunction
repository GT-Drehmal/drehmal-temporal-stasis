tag @s remove sts_crafting_thrown_pearl
tag @e[type=minecraft:item,distance=0..2,nbt={OnGround:1b,Item:{id:"minecraft:sand",Count:64b}},limit=1] add sts_crafting_item
tag @e[type=minecraft:item,distance=0..2,nbt={OnGround:1b,Item:{id:"minecraft:command_block",Count:2b,tag:{CustomModelData:1000000,RunicCatalyst:1b}}},limit=1] add sts_crafting_item
tag @e[type=minecraft:item,distance=0..2,nbt={OnGround:1b,Item:{id:"minecraft:recovery_compass",Count:1b}},limit=1] add sts_crafting_item
tag @e[type=minecraft:item,distance=0..2,nbt={OnGround:1b,Item:{id:"minecraft:clock",Count:1b}},limit=1] add sts_crafting_item

summon minecraft:item ~ ~ ~ {Item:{id:"minecraft:warped_fungus_on_a_stick",Count:1b,tag:{display:{Name:'{"text":"Runic Hourglass","color":"green","italic":false,"underlined":true}',Lore:['{"text":"An intricate mechanism infused with runic energy,","color":"dark_purple","italic":true}','{"text":"this Avsohmic creation is capable of enacting"}','{"text":"Temporal Stasis over a small area."}','{"text":"In certain regions, artificers have been spotted"}','{"text":"using a similar technology to counteract temporal magic."}','{"text":" "}','{"text":"Stasis","color":"green","italic":false}','{"text":"Right click to consume this hourglass and","color":"dark_gray"}','{"text":"claim the chunk you are standing in.","color":"dark_gray"}','{"text":"This chunk will be protected","color":"dark_gray"}','{"text":"from restoration events.","color":"dark_gray"}','{"text":" "}','{"text":"This item is consumed on use.","color":"gray"}','{"text":" "}','{"text":"Trinket","color":"green","italic":false}']},HideFlags:255,RepairCost:100000,Unbreakable:1b,CustomModelData:1001,runic_hourglass:1b,Enchantments:[{}]}}}
function stasis:playsound/runic_hourglass_crafted
function stasis:particles/runic_hourglass_crafted

kill @e[type=minecraft:item,tag=sts_crafting_item,distance=0..2]
# Prevent teleportation
kill @s