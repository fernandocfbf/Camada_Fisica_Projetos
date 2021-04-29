#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
#Carareto
#17/02/2018
#  Camada de Enlace
####################################################

# Importa pacote de tempo
import time

# Interface Física
from interfaceFisica import fisica

# enlace Tx e Rx
from enlaceRx import RX
from enlaceTx import TX

class enlace(object):
    
    def __init__(self, name):
        self.fisica      = fisica(name)
        self.rx          = RX(self.fisica)
        self.tx          = TX(self.fisica)
        self.connected   = False

    def enable(self):
        self.fisica.open()
        self.rx.threadStart()
        self.tx.threadStart()

    def disable(self):
        self.rx.threadKill()
        self.tx.threadKill()
        time.sleep(1)
        self.fisica.close()

    def sendData(self, data):
        self.tx.sendBuffer(data)
        
    def sendData_time(self, data, arquivo):
        
        tentativa = 0
        resposta_recebida = False
        
        while tentativa < 4:
            
            self.tx.sendBuffer(data)
            time.sleep(1)
            if self.rx.getIsEmpty() == True:
                arquivo.write("Sem reposta, enviando pacote novamente... \n")
                print("Sem reposta, enviando pacote novamente...")
                tentativa += 1
                time.sleep(4)
            else:
                resposta_recebida = True
                break
                
        return resposta_recebida
        
        
    def getData(self, size):
        data = self.rx.getNData(size)
        return(data, len(data))
