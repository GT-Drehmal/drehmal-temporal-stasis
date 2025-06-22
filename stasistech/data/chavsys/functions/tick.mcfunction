# execute as @a if predicate players:locations/in_terminus run function chavsys:triggers/check_triggers
# execute as @a run function chavsys:triggers/reset_all
# execute as @a if predicate players:locations/in_terminus run function chavsys:triggers/enable
# Test logic
execute as @a run function chavsys:triggers/check_triggers
execute as @a run function chavsys:triggers/reset_all
execute as @a run function chavsys:triggers/enable