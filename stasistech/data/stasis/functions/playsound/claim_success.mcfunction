playsound minecraft:block.tripwire.click_off master @a ~ ~ ~ 1 1.94
playsound minecraft:item.spyglass.use master @a ~ ~ ~ 0.24 0.5
playsound minecraft:item.brush.brushing.sand.complete master @a ~ ~ ~ 1 0
playsound minecraft:item.bone_meal.use master @s ~ ~ ~ 1 0.5
playsound minecraft:block.respawn_anchor.charge master @a ~ ~ ~ 1 0.25
playsound minecraft:block.shroomlight.place master @s ~ ~ ~ 1 1
playsound minecraft:block.copper.step master @s ~ ~ ~ 1 1
playsound minecraft:entity.splash_potion.break master @s ~ ~ ~ 1 1
summon marker ~ ~ ~ {Tags:["claimed_chunk"],data:{Active:1b}}
schedule function stasis:playsound/claim_success_1 20t