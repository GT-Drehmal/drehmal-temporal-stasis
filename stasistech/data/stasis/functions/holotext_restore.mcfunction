# Re-activate unlocked repository entries
# Holotext itself will always work, misc/repo/# only activates the lime concrete and particle indicators
# #terms.<>_total counted by misc/repo/holotext_on

execute if score #terms.stasis_total int matches 1.. in minecraft:overworld run forceload add -198 1620 -158 1661
execute if score #terms.stasis_total int matches 1.. run schedule function entities:misc/repo/0 4s

execute if score #terms.avsal_total int matches 1.. in minecraft:overworld run forceload add -198 1620 -158 1661
execute if score #terms.avsal_total int matches 1.. run schedule function entities:misc/repo/1 4s

execute if score #terms.mevir_total int matches 1.. in minecraft:overworld run forceload add -198 1620 -158 1661
execute if score #terms.mevir_total int matches 1.. run schedule function entities:misc/repo/2 4s

execute if score #terms.exodus_total int matches 1.. in minecraft:overworld run forceload add -198 1620 -158 1661
execute if score #terms.exodus_total int matches 1.. run schedule function entities:misc/repo/3 4s

execute if score #terms.core_total int matches 1.. in minecraft:overworld run forceload add -198 1620 -158 1661
execute if score #terms.core_total int matches 1.. run schedule function entities:misc/repo/8 4s

execute if score #terms.aphelion_total int matches 1.. in minecraft:overworld run forceload add -198 1620 -158 1661
execute if score #terms.aphelion_total int matches 1.. run schedule function entities:misc/repo/4 4s

execute if score #terms.inscription_total int matches 1.. in minecraft:overworld run forceload add -198 1620 -158 1661
execute if score #terms.inscription_total int matches 1.. in minecraft:lodahr run forceload add 509 -813
execute if score #terms.inscription_total int matches 1.. in minecraft:lodahr run forceload add 509 -817
execute if score #terms.inscription_total int matches 1.. in minecraft:lodahr run forceload add 522 -817
execute if score #terms.inscription_total int matches 1.. run schedule function entities:misc/repo/7 4s


execute if score #terms.ring_total int matches 1.. in minecraft:overworld run forceload add -198 1620 -158 1661
execute if score #terms.ring_total int matches 1.. in minecraft:lodahr run forceload add 509 -813
execute if score #terms.ring_total int matches 1.. in minecraft:lodahr run forceload add 509 -817
execute if score #terms.ring_total int matches 1.. in minecraft:lodahr run forceload add 522 -817
execute if score #terms.ring_total int matches 1.. run schedule function entities:misc/repo/5 4s

execute if score #terms.depot_total int matches 1.. in minecraft:overworld run forceload add -198 1620 -158 1661
execute if score #terms.depot_total int matches 1.. in minecraft:lodahr run forceload add 509 -813
execute if score #terms.depot_total int matches 1.. in minecraft:lodahr run forceload add 509 -817
execute if score #terms.depot_total int matches 1.. in minecraft:lodahr run forceload add 522 -817
execute if score #terms.depot_total int matches 1.. run schedule function entities:misc/repo/6 4s

execute if score #terms.yav_total int matches 1.. in minecraft:overworld run forceload add -198 1620 -158 1661
execute if score #terms.yav_total int matches 1.. run schedule function entities:misc/repo/9 4s

execute if score #terms.gm_total int matches 1.. in minecraft:overworld run forceload add -198 1620 -158 1661
execute if score #terms.gm_total int matches 1.. run schedule function entities:misc/repo/10 4s

execute if score #terms.halls_total int matches 1.. in minecraft:overworld run forceload add -198 1620 -158 1661
execute if score #terms.halls_total int matches 1.. run schedule function entities:misc/repo/11 4s
