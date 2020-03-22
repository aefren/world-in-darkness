import os
from pdb import Pdb

import pygame

wav = '.wav'
sounds = os.getcwd()+str('/data/sounds/')


mixer = pygame.mixer
pygame.mixer.pre_init(44100, -16, 2, 1000)
pygame.init()
pygame.mixer.set_num_channels(16)

ch0 = pygame.mixer.Channel(0) # generic.
ch1 = pygame.mixer.Channel(1) # unit move.
ch2 = pygame.mixer.Channel(2) # construction effects.
ch3 = pygame.mixer.Channel(3) #warn1.
ch4 = pygame.mixer.Channel(4) #warn2.
ch5 = pygame.mixer.Channel(5) #magic.
channels1 = [ch0, ch1, ch2, ch3, ch4, ch5]


def loadsound(soundfile, channel=ch0, path=sounds,  extention=wav, vol=1):
  channel.stop()
  if isinstance(vol, tuple): channel.set_volume(vol[0], vol[1])
  else: channel.set_volume(vol)  
  channel.play(mixer.Sound(path+soundfile+extention))
  return mixer.Sound(path+soundfile+extention).get_length()


def loadsound1(soundfile, channel=ch0, path=sounds,  extention=wav, vol=1):
  channel.stop()
  if isinstance(vol, tuple): channel.set_volume(vol[0], vol[1])
  else: channel.set_volume(vol)  
  channel.play(mixer.Sound(path+soundfile+extention))
  return mixer.Sound(path+soundfile+extention).get_length()

def play_stop(fade=100):
  for ch in channels1:
    ch.fadeout(fade)



