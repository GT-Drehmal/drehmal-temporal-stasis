## Locally test-able unlock without LuckPerms integration. Does not configure OPAC. DO NOT USE IN PRODUCTION!
scoreboard players set #enabled sts_vars 1
# Reset hourglass reception
scoreboard objectives remove sts_bool_received_hourglass
scoreboard objectives add sts_bool_received_hourglass dummy