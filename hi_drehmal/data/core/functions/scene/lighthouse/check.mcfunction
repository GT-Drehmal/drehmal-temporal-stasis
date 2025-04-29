execute store result score #tmp temp if data block 6227 134 -1765 Items[{tag:{RunicCatalyst:1b}}]
execute if score #tmp temp matches 0 run fill 6228 158 -1766 6226 160 -1764 minecraft:redstone_lamp[lit=false] replace minecraft:redstone_lamp
execute if score #tmp temp matches 0 run fill 6230 136 -1765 6230 136 -1765 minecraft:redstone_lamp[lit=false] replace minecraft:redstone_lamp

execute if score #tmp temp matches 1 run fill 6228 158 -1766 6226 160 -1764 minecraft:redstone_lamp[lit=true] replace minecraft:redstone_lamp
execute if score #tmp temp matches 1 run fill 6230 136 -1765 6230 136 -1765 minecraft:redstone_lamp[lit=true] replace minecraft:redstone_lamp