def combat(self, target):
  attacking = self.squads_position
  defending = target.squads_position
  min_mp = min([uni.moves for uni in attacking])
  dist = min([uni.dist for uni in attacking]) 
  prev_dist = 0
  
  for uni in attacking:
    moved = uni.combat_moves(prev_dist)
    dist -= moved
    prev_dist = dist
    
    if uni.check_range(defending[0]): 
      uni.combat()
