# Run on load. Checks if any of the towers that are supposed to be unlocked is not unlocked
# and verifies total tower count.
# Note: This function is only to be used at 99% (before yavhlix unlock)
scoreboard players set issue_detected debug 0

execute unless score capital_valley towers matches 1 run say [!] Capital Valley tower is supposed to be unlocked but is not [!]
execute unless score capital_valley towers matches 1 run scoreboard players set issue_detected debug 1

execute unless score av_sal towers matches 1 run say [!] Av'Sal tower is supposed to be unlocked but is not [!]
execute unless score av_sal towers matches 1 run scoreboard players set issue_detected debug 1

execute unless score palisades_heath towers matches 1 run say [!] Palisades tower is supposed to be unlocked but is not [!]
execute unless score palisades_heath towers matches 1 run scoreboard players set issue_detected debug 1

execute unless score gulf_of_drehmal towers matches 1 run say [!] Gulf of Drehmal tower is supposed to be unlocked but is not [!]
execute unless score gulf_of_drehmal towers matches 1 run scoreboard players set issue_detected debug 1

execute unless score north_tharxax towers matches 1 run say [!] North Thrarxax tower is supposed to be unlocked but is not [!]
execute unless score north_tharxax towers matches 1 run scoreboard players set issue_detected debug 1

execute unless score maels_desolation towers matches 1 run say [!] South Heartwood tower is supposed to be unlocked but is not [!]
execute unless score maels_desolation towers matches 1 run scoreboard players set issue_detected debug 1

execute unless score lorahn_kahl towers matches 1 run say [!] Lorahn'Kahl tower is supposed to be unlocked but is not [!]
execute unless score lorahn_kahl towers matches 1 run scoreboard players set issue_detected debug 1

execute unless score merijool towers matches 1 run say [!] Merijool tower is supposed to be unlocked but is not [!]
execute unless score merijool towers matches 1 run scoreboard players set issue_detected debug 1

execute unless score casai towers matches 1 run say [!] Casai tower is supposed to be unlocked but is not [!]
execute unless score casai towers matches 1 run scoreboard players set issue_detected debug 1

execute unless score spearhead_forest towers matches 1 run say [!] Spearhead tower is supposed to be unlocked but is not [!]
execute unless score spearhead_forest towers matches 1 run scoreboard players set issue_detected debug 1

execute unless score frozen_bite towers matches 1 run say [!] Frozen Bite tower is supposed to be unlocked but is not [!]
execute unless score frozen_bite towers matches 1 run scoreboard players set issue_detected debug 1

execute unless score faehrcyle towers matches 1 run say [!] Faehrcyle tower is supposed to be unlocked but is not [!]
execute unless score faehrcyle towers matches 1 run scoreboard players set issue_detected debug 1

execute unless score hellcrags towers matches 1 run say [!] Hellcrags tower is supposed to be unlocked but is not [!]
execute unless score hellcrags towers matches 1 run scoreboard players set issue_detected debug 1

execute unless score aphelion towers matches 1 run say [!] Aphelion tower is supposed to be unlocked but is not [!]
execute unless score aphelion towers matches 1 run scoreboard players set issue_detected debug 1

execute unless score lo_dahr towers matches 1 run say [!] Lo'Dahr tower is supposed to be unlocked but is not [!]
execute unless score lo_dahr towers matches 1 run scoreboard players set issue_detected debug 1

execute unless score dawn_island towers matches 1 run say [!] Dawn tower is supposed to be unlocked but is not [!]
execute unless score dawn_island towers matches 1 run scoreboard players set issue_detected debug 1

execute unless score dusk_island towers matches 1 run say [!] Dusk tower is supposed to be unlocked but is not [!]
execute unless score dusk_island towers matches 1 run scoreboard players set issue_detected debug 1

execute unless score sahd towers matches 1 run say [!] Sahd tower is supposed to be unlocked but is not [!]
execute unless score sahd towers matches 1 run scoreboard players set issue_detected debug 1

execute unless score black_jungle towers matches 1 run say [!] Black Jungle tower is supposed to be unlocked but is not [!]
execute unless score black_jungle towers matches 1 run scoreboard players set issue_detected debug 1

execute unless score purity_peaks towers matches 1 run say [!] Purity Peaks tower is supposed to be unlocked but is not [!]
execute unless score purity_peaks towers matches 1 run scoreboard players set issue_detected debug 1

execute unless score grand_pike_canyon towers matches 1 run say [!] Grand Pike tower is supposed to be unlocked but is not [!]
execute unless score grand_pike_canyon towers matches 1 run scoreboard players set issue_detected debug 1

execute unless score veruhkt_plateau towers matches 1 run say [!] Veruhkt tower is supposed to be unlocked but is not [!]
execute unless score veruhkt_plateau towers matches 1 run scoreboard players set issue_detected debug 1 

execute unless score highfall_tundra towers matches 1 run say [!] Highfall tower is supposed to be unlocked but is not [!]
execute unless score highfall_tundra towers matches 1 run scoreboard players set issue_detected debug 1 

execute unless score ebony_veldt towers matches 1 run say [!] Ebony Veldt tower is supposed to be unlocked but is not [!]
execute unless score ebony_veldt towers matches 1 run scoreboard players set issue_detected debug 1 

execute unless score ebonfire towers matches 1 run say [!] Mt.Ebonfire tower is supposed to be unlocked but is not [!]
execute unless score ebonfire towers matches 1 run scoreboard players set issue_detected debug 1 

execute unless score anyr_nogur towers matches 1 run say [!] Anyr'Nogur tower is supposed to be unlocked but is not [!]
execute unless score anyr_nogur towers matches 1 run scoreboard players set issue_detected debug 1 

execute unless score nimahj_swamp towers matches 1 run say [!] Nimahj tower is supposed to be unlocked but is not [!]
execute unless score nimahj_swamp towers matches 1 run scoreboard players set issue_detected debug 1 

execute unless score akhlo_rohma towers matches 1 run say [!] Akhlo'rohma tower is supposed to be unlocked but is not [!]
execute unless score akhlo_rohma towers matches 1 run scoreboard players set issue_detected debug 1 

execute unless score south_tharxax towers matches 1 run say [!] South Tharxax tower is supposed to be unlocked but is not [!]
execute unless score south_tharxax towers matches 1 run scoreboard players set issue_detected debug 1 

execute unless score heartwood towers matches 1 run say [!] North Heartwood tower is supposed to be unlocked but is not [!]
execute unless score heartwood towers matches 1 run scoreboard players set issue_detected debug 1 

execute unless score carmine towers matches 1 run say [!] Carmine tower is supposed to be unlocked but is not [!]
execute unless score carmine towers matches 1 run scoreboard players set issue_detected debug 1 

# Continue exerting pain upon myself
scoreboard players set tower_total debug 0
execute if score aphelion towers matches 1 run scoreboard players add tower_total debug 1
execute if score av_sal towers matches 1 run scoreboard players add tower_total debug 1
execute if score black_jungle towers matches 1 run scoreboard players add tower_total debug 1
execute if score capital_valley towers matches 1 run scoreboard players add tower_total debug 1
execute if score carmine towers matches 1 run scoreboard players add tower_total debug 1
execute if score casai towers matches 1 run scoreboard players add tower_total debug 1
execute if score dawn_island towers matches 1 run scoreboard players add tower_total debug 1
execute if score dusk_island towers matches 1 run scoreboard players add tower_total debug 1
execute if score ebonfire towers matches 1 run scoreboard players add tower_total debug 1
execute if score ebony_veldt towers matches 1 run scoreboard players add tower_total debug 1
execute if score faehrcyle towers matches 1 run scoreboard players add tower_total debug 1
execute if score frozen_bite towers matches 1 run scoreboard players add tower_total debug 1
execute if score grand_pike_canyon towers matches 1 run scoreboard players add tower_total debug 1
execute if score gulf_of_drehmal towers matches 1 run scoreboard players add tower_total debug 1
execute if score heartwood towers matches 1 run scoreboard players add tower_total debug 1
execute if score hellcrags towers matches 1 run scoreboard players add tower_total debug 1
execute if score highfall_tundra towers matches 1 run scoreboard players add tower_total debug 1
execute if score lo_dahr towers matches 1 run scoreboard players add tower_total debug 1
execute if score lorahn_kahl towers matches 1 run scoreboard players add tower_total debug 1
execute if score maels_desolation towers matches 1 run scoreboard players add tower_total debug 1
execute if score merijool towers matches 1 run scoreboard players add tower_total debug 1
execute if score nimahj_swamp towers matches 1 run scoreboard players add tower_total debug 1
execute if score north_tharxax towers matches 1 run scoreboard players add tower_total debug 1
execute if score palisades_heath towers matches 1 run scoreboard players add tower_total debug 1
execute if score purity_peaks towers matches 1 run scoreboard players add tower_total debug 1
execute if score sahd towers matches 1 run scoreboard players add tower_total debug 1
execute if score south_tharxax towers matches 1 run scoreboard players add tower_total debug 1
execute if score spearhead_forest towers matches 1 run scoreboard players add tower_total debug 1
execute if score veruhkt_plateau towers matches 1 run scoreboard players add tower_total debug 1
execute if score yavhlix towers matches 1 run scoreboard players add tower_total debug 1
execute if score akhlo_rohma towers matches 1 run scoreboard players add tower_total debug 1
execute if score anyr_nogur towers matches 1 run scoreboard players add tower_total debug 1

execute unless score tower_total debug = count_all towers run say [!] Tower count_all does not match actual number of towers unlocked [!]
execute unless score tower_total debug = count_all towers run scoreboard players set issue_detected debug 1
execute if score issue_detected debug matches 1.. run say # <@&1230184718574686259> Immediate attention requested. **Terminus scoreboard corruption has been detected!**

execute if score tower_total debug = count_all towers if score issue_detected debug matches 0 run say [Terminus Health Check] All checks passed.
