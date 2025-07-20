say [Temporal Stasis] Rolling back progression scoreboard values...

# spawn tomb
scoreboard players reset #stomb_p bool

# repository campfire door
scoreboard players reset #avsys_p1 bool

# sal'mevir
scoreboard players reset #sal_top bool
scoreboard players reset #sal_bedrock bool

# exodus citadel
scoreboard players set #exodusdoor timer 0
scoreboard players set @e[tag=vaultPower] vaultPower 0
scoreboard players set #electrowater y 0
scoreboard players set #electrowater z 0
scoreboard players set #electrowater x 0
scoreboard players set #mythbreakerdoor timer 0
scoreboard players set #exodustank y 0
scoreboard players set #exodustank x 0
scoreboard players set #exodustank z 0
scoreboard players set #exodusbigdoor z 0
scoreboard players set #exodusbigdoor y 0

# av'sal/administrative wing armorless door
scoreboard players reset #avsys_p2 bool

# aphelion shuttle
scoreboard players set #shuttleState num 0

# aphelion fuel eject
scoreboard players reset #ejectDoor bool
scoreboard players reset #ejectConfirm bool

# lodahr tower drop
scoreboard players reset #towerdrop bool

# core facility
scoreboard players set #coreportal x 0
scoreboard players set #coreportal y 0

# numencore/mythbreaker run
scoreboard players reset #mb_place_part bool
scoreboard players reset #coretrack int
scoreboard players reset #core_ani int
scoreboard players reset #core_door bool
scoreboard players reset #coretrigs int
scoreboard players reset #cmtrig bool
scoreboard players reset #cmtrig2 bool
scoreboard players reset #cmtrig3 bool
scoreboard players reset #coreo1 bool
scoreboard players reset #coreo2 bool
scoreboard players reset #mb_picked bool
scoreboard players reset #core_broke bool

# yavhlix
scoreboard players reset #yav.l1 bool
scoreboard players reset #yav.l2 bool
scoreboard players reset #yav.l3 bool
scoreboard players reset #yav.levers int

# tethlaen
scoreboard players reset #teth_dead? bool

# silent thing/azimuth labs
scoreboard players set #lunalaserdeaths x 0
scoreboard players set #lunasparks bool 0
scoreboard players set #dia_lunbase timer 0
scoreboard players set #stop_lunarbase bool 0
scoreboard players reset #myth_dia10_3 bool
scoreboard players reset #myth_dia10_4 bool
scoreboard players reset #myth_dia10_5 bool
scoreboard players set #anyrportal bool 0
scoreboard players set #godmachine x 0
scoreboard players set #godmachine z 0
scoreboard players set #godmachine y 0
scoreboard players set #anyrtp timer 0

# resonant thing/resonant halls
scoreboard players reset #myth_dia11_2 bool
scoreboard players set #myth_dia11_3 bool 0
scoreboard players set #retinaportal bool 0
scoreboard players set #retinatp timer 0
scoreboard players set #retinacheck bool 0
scoreboard players set #retinacont bool 0

# rhythmic thing/the court
scoreboard players set #stop_stasisfacility bool 0
scoreboard players set #myth_dia12_2 bool 0
scoreboard players set #myth_dia12_3 bool 0
scoreboard players set #muralanim timer 0
scoreboard players set #stop_muralroom bool 0
scoreboard players set #myth_dia12_4 bool 0
scoreboard players set #myth_dia12_5 bool 0
scoreboard players set #tmbportal timer 0
scoreboard players set #tmb_picked? bool 1
scoreboard players set #myth_dia12_6 bool 0
scoreboard players set #courtportal bool 0
scoreboard players set #courtportal timer 0
scoreboard players set #myth_dia12_7 bool 0
scoreboard players set #stop_hovadwin bool 0
scoreboard players set #voidportal bool 0
scoreboard players set #voidportal timer 0

# hovadchear and ultva
scoreboard players reset #hovadhallintro bool
scoreboard players reset #hovadbossintro timer
scoreboard players reset #fightinghovad bool
scoreboard players reset #hovadspawned bool
scoreboard players reset #ultvamusic bool

# the void
scoreboard players set #myth_dia13_1 bool 0
scoreboard players set #myth_dia13_2 bool 0
scoreboard players set #myth_dia13_3 bool 0
scoreboard players set #myth_dia13_4 bool 0
scoreboard players set #myth_dia13_5 bool 0
scoreboard players set #emmportal timer 0
scoreboard players set #returnportal bool 0
scoreboard players set #returnportal z 0
scoreboard players set #returnportal timer 0
scoreboard players set #gearportal timer 0 

# emissary/drehn
scoreboard players reset #em_fight_active? bool
scoreboard players reset #em_fight_done? bool
scoreboard players reset #em_fight_rejoin_p? bool
scoreboard players reset #empty_arena? temp

# ossein
scoreboard players reset #ossein_dead? bool

# vehrniis/bernice
scoreboard players set #berndoor y 0
scoreboard players reset #bernice_cleared? bool
scoreboard players reset #bern_active? bool
scoreboard players reset #bern_no_spawn? bool
scoreboard players set #berniceSpawned bool 0

# foundry
scoreboard players reset #fdry.stone_earned? bool
scoreboard players reset #fdry.reset_room? bool
scoreboard players reset #fdry_completed? bool
scoreboard players reset #failed_wave foundry
scoreboard players reset #foundry.glow bool
scoreboard players reset #fdry_lev1? bool
scoreboard players reset #fdry_lev2? bool
scoreboard players reset #fdry_lev3? bool
scoreboard players reset #fdry_door int
scoreboard players reset #znth_lights_on bool

# lodahr amethyst portals
scoreboard players set #bp_portal timer 0
scoreboard players set #bp_portal bool 0
scoreboard players reset #bpalace_travelled? bool
scoreboard players set #ark_portal timer 0
scoreboard players set #ark_portal bool 0
scoreboard players set #lai_portal timer 0
scoreboard players set #lai_portal bool 0
scoreboard players set #loe_portal timer 0
scoreboard players set #loe_portal bool 0
scoreboard players reset #alch_on? bool
scoreboard players reset #alch_active? bool
scoreboard players reset #alch_portal bool
scoreboard players reset #alch_portal bool
scoreboard players reset #alch_portal timer
scoreboard players set #stump_portal timer 0
scoreboard players set #stump_portal bool 0

# syzygy
scoreboard players reset #szy_complete bool
scoreboard players reset #syzygy_spawned? bool
scoreboard players set #syzygytrials timer 0
scoreboard players set #syzygytrials y 0
scoreboard players reset #syzygy_progress? bool

# rihelma trial
scoreboard players reset #rihelmalight1 bool
scoreboard players reset #rihelmalight2 bool
scoreboard players reset #rihelmalight3 bool
scoreboard players reset #rihelmalight4 bool
scoreboard players reset #rihelmalight5 bool
scoreboard players reset #rihelmalight6 bool
scoreboard players reset #rihelmalights int
scoreboard players reset #rihelmabeams int

# vayniklah trial
scoreboard players reset #syzygy_num_1 int
scoreboard players reset #syzygy_num_2 int
scoreboard players reset #syzygy_num_3 int
scoreboard players reset #syzygy_num_4 int
scoreboard players reset #syzygy_nums? bool
scoreboard players reset #trial_com_nums bool

# lai trial
scoreboard players reset #trial_com_lai bool

# khive trial
scoreboard players set #trial_com_khive bool 0

# nahyn trial
scoreboard players reset #syzygy_progress? bool
scoreboard players reset #syzygy_maze? bool
scoreboard players set #trial_com_nahyn bool 0

# dahr trial
scoreboard players set #dahr_pearl_count int 0
scoreboard players set #dahr_pearl_1 bool 0
scoreboard players set #dahr_pearl_2 bool 0
scoreboard players set #dahr_pearl_3 bool 0
scoreboard players set #dahr_pearl_4 bool 0
scoreboard players set #dahr_pearl_5 bool 0

# aeongale
scoreboard players set #aeongale x 0
scoreboard players set #aeoncap1 x 0
scoreboard players set #aeoncap1 z 0
scoreboard players set #aeongaledoor x 0
scoreboard players set #aeongaledoor y 0

# dahroehl
scoreboard players reset #dahroehl.rb1 timer
scoreboard players reset #dahroehl.rb2 timer
scoreboard players reset #dahroehl.riddle bool

# misc / lost and found variables
scoreboard players reset #khive_scroll bool
scoreboard players reset #wdespawn timer

scoreboard players reset #played_pigstep? bool

# Coven of Potentia & bpalace fights
scoreboard players reset #rhalon_triggered bool
scoreboard players reset #bpalace.tevus bool
scoreboard players reset #bpalace.cyard bool

scoreboard players reset #wrathfrag? bool

scoreboard players reset #sunmoon0_active? bool
scoreboard players reset #sunmoon0 despawn_timer
scoreboard players reset #sunmoon0_dead? bool
scoreboard players reset #sunmoon1_active? bool
scoreboard players reset #sunmoon1 despawn_timer
scoreboard players reset #sunmoon1_dead? bool
scoreboard players reset #sunmoon2_active? bool
scoreboard players reset #sunmoon2 despawn_timer
scoreboard players reset #sunmoon2_dead? bool
scoreboard players reset #sunmoon3_active? bool
scoreboard players reset #sunmoon3 despawn_timer
scoreboard players reset #sunmoon3_dead? bool
scoreboard players reset #sunmoon4_active? bool
scoreboard players reset #sunmoon4 despawn_timer
scoreboard players reset #sunmoon4_dead? bool

scoreboard players reset #loe_p1 bool

scoreboard players reset #av_ani bool
scoreboard players reset #ad_ani bool
scoreboard players reset #ex_ani bool
scoreboard players reset #lo_ani bool
scoreboard players reset #mev_ani bool

scoreboard players reset #daylight_on bool
scoreboard players reset #sal_entered bool

scoreboard players reset #ark_flag? bool
scoreboard players reset #t.vir.spawned? bool

scoreboard players reset #fzy_picked? bool

scoreboard players reset #b.passive_alive? bool

# Av'Sal repository holotext "pressure plate" appearance
function stasis:holotext_restore

say [Temporal Stasis] Rollback complete.
