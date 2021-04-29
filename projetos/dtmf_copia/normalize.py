# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 22:20:15 2020

@author: ferna
"""

from pydub import AudioSegment

def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)

sound = AudioSegment.from_file("f.wav", "wav")
normalized_sound = match_target_amplitude(sound, 1)
normalized_sound.export("nomrmalizedAudio.wav", format="wav")