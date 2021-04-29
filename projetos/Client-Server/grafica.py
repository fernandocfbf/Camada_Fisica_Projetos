# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 16:15:24 2020

@author: Fernando
"""


from enlace import *

from tkinter import *
from tkinter.ttk import *
import re
from tqdm.auto import tqdm
from tkinter import Label
import time
from tkinter.filedialog import askopenfile


# define variávei none
volta = "COM5"
ida = "COM3"                  # Windows(variacao de)
imageW = None
file_name = None
txSize = None


root = Tk() 
root.geometry('400x150') 

progress = Progressbar(root, orient = HORIZONTAL, 
              length = 180, mode = 'determinate') 
file_text = Text(root, height=0.5, width=22)

def open_file(): 
    global file_name
    file = askopenfile(mode ='r', filetypes =[("Image File",'.png')]) 
    if file is not None: 
        file_name = file.name
        file_text.insert(END, file_name)
        print(file_name)
        
def main_ida():
    global imageW
    global txSize
    
    try:
        progress['value'] = 5
        root.update_idletasks()
        
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com = enlace(ida)
    
        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com.enable()
        print("Comunicação de ida estabelecida com sucesso!")
        
        progress['value'] = 25
        root.update_idletasks()
    
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        
        #aqui você deverá gerar os dados a serem transmitidos. 
        #seus dados a serem transmitidos são uma lista de bytes a serem transmitidos. Gere esta lista com o 
        #nome de txBuffer. Esla sempre irá armazenar os dados a serem enviados.
        imageR = str(file_name)
        imageW = "downloadArduino.png"
        
        
        # <------------------------------------------------ IDA ------------------------------------------------------------>
        
        
        #txBuffer = bytes([255])
        txBuffer = open(imageR, "rb").read()
    
        #faça aqui uma conferência do tamanho do seu txBuffer, ou seja, quantos bytes serão enviados.
        print("Transferindo dados: {0} byts".format(len(txBuffer)))
    
        #finalmente vamos transmitir os tados. Para isso usamos a funçao sendData que é um método da camada enlace.
        #faça um print para avisar que a transmissão vai começar.
        #tente entender como o método send funciona!
        
        #print("Início da Transmissão...")
        
        com.sendData(txBuffer)
        
        time.sleep(2) #sem isso não da tempo de enviar a mensagem e por isso o txSize seria 0

        # A camada enlace possui uma camada inferior, TX possui um método para conhecermos o status da transmissão
        # Tente entender como esse método funciona e o que ele retorna
        txSize = int(com.tx.getStatus())
        
        print("Bits enviados: {0} | Bits desejados: {1}".format(txSize, len(txBuffer)))
       
        #Agora vamos iniciar a recepção dos dados. Se algo chegou ao RX, deve estar automaticamente guardado
        #Observe o que faz a rotina dentro do thread RX
        #print um aviso de que a recepção vai começar.
        
        progress['value'] = 50
        root.update_idletasks()
        
        com.disable()
        print("Com de ida desabilidata!")
        
    except:
        print("ops! :-\\")
        if com is not None:
            com.disable()
            

# -------------------------------------------------------------------------------------------------------------------------
                     

def main_volta():
    try:

        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com_volta = enlace(volta)
    
        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com_volta.enable()
        print("Comunicação de volta estabelecida com sucesso!")
    
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        
        progress['value'] = 75
        root.update_idletasks()
        
        # <------------------------------------------------ VOLTA ------------------------------------------------------->
        print("Início da recepção de dados...")
        print("Número de dados recebidos: {0}".format(txSize))
        
        #Será que todos os bytes enviados estão realmente guardadas? Será que conseguimos verificar?
        #Veja o que faz a funcao do enlaceRX  getBufferLen
        tamanho_recebido = com_volta.rx.getBufferLen()
        print("tamanho recebido: {0}".format(tamanho_recebido))
        #acesso aos bytes recebidos
        rxBuffer, nRx = com_volta.getData(txSize)
        print(rxBuffer)
        
        if int(nRx) == int(txSize):
            #arquivo chegou inteiro!
            print("Salvando dados no arquivo")
            print(" - {}".format(imageW))
            f = open(imageW, "wb")
            f.write(rxBuffer)
            
            progress['value'] = 90
            root.update_idletasks()
            
            print(rxBuffer)
            
            f.close()
        
            # Encerra comunicaçãos
            print("-------------------------")
            print("Comunicação encerrada")
            print("-------------------------")
            com_volta.disable()
            
            progress['value'] = 100
            root.update_idletasks()
        
        else:
            print("ops! arquivos diferentes!")
            com_volta.disable()
    
        
    except:
        print("ops! :-\\")
        com_volta.disable()
    
def ida_e_volta():
    print("INICIALIZANDO IDA")
    main_ida()
    print("INICIALIZANDO VOLTA")
    main_volta()


btn = Button(root, text ='Open', command = lambda:open_file()) 
btn.pack()     

proc = Button(root, text = 'Process', command = lambda: ida_e_volta()) 
proc.pack() 

root.title("Client - Server")

btn.place(relx = 0.2, x =20, y = 20, anchor = NE)
proc.place(relx = 0.2, x =20, y = 60, anchor = NE)

file_text.pack(pady = 22)
progress.pack(pady =0.15)

mainloop()