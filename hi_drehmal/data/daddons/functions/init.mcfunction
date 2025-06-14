## To be called by core:init
# Let player not go through sancheck the second time they hear Mythos name
scoreboard objectives add sts_heard_name dummy
# Out of bounds warning variable
# Counts upward to 60t (3s)
scoreboard objectives add oob_warning dummy