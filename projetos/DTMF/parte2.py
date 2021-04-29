# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 16:56:27 2020

@author: ferna
"""

import peakutils
import numpy as np
from scipy import signal
from scipy.fftpack import fft, fftshift
import matplotlib.pyplot as plt
import sounddevice as sd
import time
import soundfile as sf


def calcFFT(signal, fs):
    N  = len(signal)
    T  = 1/fs
    xf = np.linspace(-1.0/(2.0*T), 1.0/(2.0*T), N)
    yf = fft(signal)

    return (xf, fftshift(yf))


def determinaPicos(x, y):
    
    #determina o index
    index = peakutils.indexes(np.abs(y), thres=0.8, min_dist=50)
    
    #cria a lista de resposta
    resposta = []
    
    #salva as frequencias numa lista
    for freq in x[index]:
        resposta.append(freq)
        
    return resposta

def leOnda(arquivo):
    fs = 44100   # taxqa de amostagem (sample rate)
    sd.default.samplerate = fs
    sd.default.channels = 1
    audio, samplerate = sf.read(arquivo)
    
    return audio

def eliminaNegativos(lista_picos):
    
    #cria uma lista de resposta
    lista_resposta = []
    
    
    for pico in lista_picos:
        
        #se o pico for negativo nao adiciona na lista final
        if int(pico) < 0:
            pass
        
        #se for positivo add na lista final
        else:
            lista_resposta.append(pico)
            
    return lista_resposta

def determinaTecla(dicionario, picos):
    
    achou = False
    
    numero = -1
    
    if len(picos) < 2:
        return numero
    
    #enquanto nao achar o numero
    while achou == False:
        
        for numero in dicionario: 
            
            #lista de frequencias
            lista_freq = dicionario[numero]
            
            f1 = int(lista_freq[0])
            f2 = int(lista_freq[1])
            
            if (f1 > picos[0] - 10 and f1 < picos[0] + 10) or (f1 > picos[1] - 10 and f1 < picos[1] + 10):
                achou_f1 = True
            else:
                achou_f1 = False
                
            if (f2 > picos[0] - 10 and f2 < picos[0] + 10) or (f2 > picos[1] - 10 and f2 < picos[1] + 10):
                achou_f2 = True
            else:
                achou_f2 = False
            
            if achou_f1 == True and achou_f2 == True:
                achou = True
                break
            
            else:
                pass
    
    return numero

def record():
    
    #frequencia do sinal
    fs = 44100
    
    #executa o som do sinal
    wave = sd.rec(fs*3, channels=1)
    
    #função necessária 
    sd.wait()
    
    return wave


tabela = {
        "1":["697","1209"],
        "2":["697","1336"],
        "3":["697","1477"],
        "A":["697","1633"],
        "4":["770","1209"],
        "5":["770","1336"],
        "6":["770","1477"],
        "B":["770","1633"],
        "7":["852","1209"],
        "8":["852","1336"],
        "9":["852","1477"],
        "C":["852","1633"],
        "X":["941","1209"],
        "0":["941","1336"],
        "#":["941","1477"],
        "D":["941","1633"],
    }
        
a = input("preparar para gravar o sinal")

print("Gravando...")
wave = record()

time.sleep(4)

tempo = np.linspace(0,3,len(wave))

plt.plot(tempo, wave)
plt.title("WAVE")
plt.show()

x, y = calcFFT(wave, 44100)

plt.plot(x,y)
plt.title("FOURIER WAVE")
plt.xlim(-3000,3000)
plt.show()






# #salva o sinal da variável w1
# wave_gerada = leOnda('gravacao_bruna.wav')

# wave_gerada = wave_gerada[198450:220500]

# #calcula o fourier do sinal
# x, y = calcFFT(wave_gerada, 22050)

# tempo = np.linspace(0, 1, 22050)

# plt.plot(tempo, wave_gerada)
# plt.title("Sinal escutado")

# plt.show()

# plt.plot(x, y)
# plt.title("Fourier do sinal escutado")
# plt.show()

# #plota o gráfico do fourier
# plotaGraficoFourier(x, y, "Fourier do sinal escutado", "Tempo [s]", "Amplitude")

#caclula as frequências de pico
picos = determinaPicos(x, y)

#pega somente os picos com valores positivos
somente_positivos = eliminaNegativos(picos)

# tecla = determinaTecla(tabela, somente_positivos)

# print("A tecla selecionada foi: {0}".format(tecla))


