import accessible_output2 as ao2


speaker = 'NVDA'
for i in ao2.get_output_classes():
  #print(i.name)
  if i.name == speaker: sp = i()