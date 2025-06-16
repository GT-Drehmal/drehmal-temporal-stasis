## Should be called by core:reset/start
# Stasis - Should NOT be restored
scoreboard objectives remove sts_heard_name
scoreboard objectives remove oob_warning
scoreboard players set #story_disabled? bool 0

function daddons:init