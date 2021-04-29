import numpy as np
from scipy import signal
from scipy.fftpack import fft, fftshift
import matplotlib.pyplot as plt
import sounddevice as sd
import time



def geraDicionario():

    #dicionario das frequências
    dicionario_resposta = {
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

    return dicionario_resposta

def generateSin(freq, time, fs):

    #número de pontos | fs é o numero de pontos por segundo
    n = time*fs

    #eixo do tempo
    x = np.linspace(0.0, time, n)

    #cria a senoide
    s = np.sin(freq*x*2*np.pi)

    return (x, s)

def devolveListaDeFrequencia(dicionario, discado):

    #pega a lista das frequencias do valor desejado
    frequencias = dicionario[discado] 

    return frequencias


def geraSinalDesejado(lista_de_frequencias):

    #pega a frequência1, ou seja, a frequência da linha na tabela
    freq1 = int(lista_de_frequencias[0])

    #pega a frequencia2, ou seja, a frequência da coluna na tabela
    freq2 = int(lista_de_frequencias[1])

    #gera a primeira senoide
    x, senoide1 = generateSin(freq1, 6, 44100)

    #gera a segunda senoide1
    x, senoide2 = generateSin(freq2, 6, 44100)

    #gera o sinal somado das senoides
    sinalSomado = senoide1 + senoide2

    return (x, senoide1, senoide2, sinalSomado)

def plotaGrafico(eixoX, eixoY, titulo, xlabel, ylabel):
    
    plt.plot(eixoX, eixoY)
    plt.title(titulo)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xlim(1, 1.005)
    plt.show()
    
    return
    
def play(sinal):
    
    #frequencia do sinal
    fs = 44100
    
    #executa o som do sinal
    sd.play(sinal, fs)
    
    #função necessária 
    sd.wait()
    
    return

def calcFFT(signal, fs):
    N  = len(signal)
    T  = 1/fs
    xf = np.linspace(-1.0/(2.0*T), 1.0/(2.0*T), N)
    yf = fft(signal)

    return (xf, fftshift(yf))
    

#gera o dicionario das frequências
tabela = geraDicionario()

#captura o número a ser discado
valor_discado = input("Digite um número entre [0:9]: ")

#captura as frequências do sinal
frequencias = devolveListaDeFrequencia(tabela, valor_discado)

#devolve os sinais separados, o somado e a linha do tempo
tempo, s1, s2, somado = geraSinalDesejado(frequencias)

#gera o gráfico somado
plotaGrafico(tempo, somado, "Sinal resultante", "Tempo [s]", "Amplitude")






