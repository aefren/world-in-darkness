import os
from pdb import Pdb

import pygame

wav = '.wav'
path = os.getcwd() + str('/data/sounds/')


mixer = pygame.mixer
pygame.mixer.pre_init(frequency=44100, size=16, channels=2, buffer=1000)
pygame.init()
pygame.mixer.set_num_channels(16)

CHT1 = pygame.mixer.Channel(0)  # generic.
CHT2 = pygame.mixer.Channel(1)  # unit move.
CHT3 = pygame.mixer.Channel(2)  # construction effects.
CHTE1 = pygame.mixer.Channel(3)  # warn1.
CHTE2 = pygame.mixer.Channel(4)  # warn2.
CHTE3 = pygame.mixer.Channel(5)  # magic.
CHUNE1 = pygame.mixer.Channel(6)  # magic.
channels1 = [CHT1, CHT2, CHT3, CHTE1, CHTE2, CHTE3]


def loadsound(soundfile, channel=CHT1, path=path, extention=wav, vol=1):
    channel.stop()
    if isinstance(vol, tuple): channel.set_volume(vol[0], vol[1])
    else: channel.set_volume(vol)
    channel.play(mixer.Sound(path + soundfile + extention))
    return mixer.Sound(path + soundfile + extention).get_length()


def loadsound1(soundfile, channel=CHT1, path=path, extention=wav, vol=1):
    channel.stop()
    if isinstance(vol, tuple): channel.set_volume(vol[0], vol[1])
    else: channel.set_volume(vol)
    channel.play(mixer.Sound(path + soundfile + extention))
    return mixer.Sound(path + soundfile + extention).get_length()


def play_stop(fade=100):
    for ch in channels1:
        ch.fadeout(fade)
