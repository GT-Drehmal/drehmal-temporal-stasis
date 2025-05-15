scoreboard players remove @s sts_claims 1

# Calculate the remaining # of claims for display
scoreboard players operation #remaining sts_temp = #max sts_claims
scoreboard players operation #remaining sts_temp += @s sts_extra_claims
scoreboard players operation #remaining sts_temp -= @s sts_claims

# Feedback
tellraw @s [{"text":"Success! ","color":"yellow","bold":true},{"text":"Temporal Stasis has been","color":"gray","bold":false},{"text":" disabled ","color":"dark_red","bold":false,"italic":true},{"text":"for the current chunk. You now have ","color":"gray","bold":false,"italic":false},{"score":{"name":"#remaining","objective":"sts_temp"},"color":"white","bold":false,"italic":false},{"text":"/","color":"gray","bold":false,"italic":false},{"score":{"name":"#playermax","objective":"sts_temp"},"color":"gray","bold":false,"italic":false},{"text":" claims.","color":"gray","bold":false,"italic":false}]

function stasis:playsound/unclaim_success
function stasis:particles/unclaim_success

item replace entity @s weapon.mainhand with air