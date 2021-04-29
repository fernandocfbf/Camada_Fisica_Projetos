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
import soundfile   as sf


def calcFFT(signal, fs):
    N  = len(signal)
    T  = 1/fs
    xf = np.linspace(-1.0/(2.0*T), 1.0/(2.0*T), N)
    yf = fft(signal)

    return (xf, fftshift(yf))

def plotaGraficoFourier(eixoX, eixoY, titulo, xlabel, ylabel):
    
    plt.plot(eixoX, eixoY)
    plt.title(titulo)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xlim(0, 5000)
    plt.show()
    
    return

def determinaPicos(x, y):
    
    #determina o index
    index = peakutils.indexes(np.abs(y), thres=0.35, min_dist=50)
    
    #cria a lista de resposta
    resposta = []
    
    #salva as frequencias numa lista
    for freq in x[index]:
        resposta.append(freq)
        
    return resposta

def plotaGraficoNovo(eixoX, eixoY, titulo, xlabel, ylabel):
    
    plt.plot(eixoX, eixoY)
    plt.title(titulo)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xlim(0.25,0.255)
    plt.show()
    
    return

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

def nova(picos, dic):
    
    lista = ["697","1209","1336","1477","1633","770","852","941"]
    
    f1 = int(picos[0])
    
    freq1 = 0
    dif_atual1 = 1000000000
    
    for value in lista:
        if abs(f1-int(value)) <= dif_atual1:
            dif_atual1 = abs(f1-int(value))
            freq1 = int(value)

    
    f2 = int(picos[1])
    
    freq2 = 0
    dif_atual2 = 1000000000
    
    for value in lista:
        if abs(f2-int(value)) <= dif_atual2:
            dif_atual2 = abs(f2-int(value))
            freq2 = int(value)
            
    freq1 = str(freq1)
    freq2 = str(freq2)
    
    for chave in dic:
        if dic[chave] == [freq1, freq2] or dic[chave] == [freq2, freq1]:
            return chave, freq1, freq2
    
    

#dicionario das frequências
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

#executa o arquivo da parte1
exec(open('parte1.py').read())

#salva o sinal da variável w1
wave_gerada = leOnda('teste.wav')

#calcula o fourier do sinal
x, y = calcFFT(wave_gerada, 44100)

tempo = np.linspace(0, 1, len(wave_gerada))

#gera o gráfico somado
plotaGraficoNovo(tempo, wave_gerada, "Sinal escutado", "Tempo [s]", "Amplitude")

#plota o gráfico do fourier
plotaGraficoFourier(x, y, "Fourier do sinal escutado", "Tempo [s]", "Amplitude")

# #caclula as frequências de pico
picos = determinaPicos(x, y)

# # #pega somente os picos com valores positivos
somente_positivos = eliminaNegativos(picos)

print("")
print("---------INDENTIFICANDO PICOS---------")
print("PICO1 = {0}\nPICO2 = {1}".format(somente_positivos[0],somente_positivos[1]))
print("--------------------------------------")
print("")

tecla, p1, p2 = nova(somente_positivos, tabela)

print("")
print("---------ENCONTRANDO PICOS CORRESPONDENTES---------")
print("PICO1 = {0}\nPICO2 = {1}".format(p1,p2))
print("---------------------------------------------------")
print("")

print("")
print("---------TECLA CORRESPONDENTE---------")
print("TECLA = {0}".format(tecla))
print("--------------------------------------")
print("")


