import accessible_output2 as ao2


speaker = 'NVDA'
sp = None
for i in ao2.get_output_classes():
    if i.name == speaker: sp = i()
if sp == None:
    print(f"not screen reader found.")
    Pdb().set_trace()
