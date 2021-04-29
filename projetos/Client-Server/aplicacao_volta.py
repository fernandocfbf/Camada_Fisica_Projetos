#####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 


from enlace import *
from tkinter import *
from tkinter.ttk import *
import re
from tqdm.auto import tqdm
from tkinter import Label
import time
from tkinter.filedialog import askopenfile
# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
volta = "COM3"          # Windows(variacao de)

root = Tk() 
root.geometry('400x150') 

progress = Progressbar(root, orient = HORIZONTAL, 
              length = 180, mode = 'determinate') 


def main_volta():
        
    progress['value'] = 5
    root.update_idletasks()
    
    #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
    #para declarar esse objeto é o nome da porta.
    com_volta = enlace(volta)

    # Ativa comunicacao. Inicia os threads e a comunicação seiral 
    com_volta.enable()
    
    print("------------------------------------")
    
    print("ATIVANDO PORTA DE RECEPÇÃO")
    

    #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
    
    progress['value'] = 30
    root.update_idletasks()
    
    # <------------------------------------------------ VOLTA ------------------------------------------------------->
    
    print("------------------------------------")
    
    print("ESTABELECENDO COMUNICAÇÃO PRÉVIA...")
    
    print("------------------------------------")
    
    
    
    tamanho_recebido = False
    tamanho = 0
    data = None
    while tamanho_recebido == False:
        if com_volta.rx.getBufferLen() == 2:
            
            data, n = com_volta.getData(2)
            tamanho = int.from_bytes(data, "big")
            tamanho_recebido = True
        else:
            pass
        
    start = time.time()
    com_volta.rx.clearBuffer()
    
    while True:
        if com_volta.rx.getBufferLen() == 0:
            print("ESPERANDO O ARQUIVO")
            
            print("------------------------------------")
            
            time.sleep(0.2)
            
        else:
            time.sleep(1)
            break
        
    
    tamanho_recebido = com_volta.rx.getBufferLen()
    
    #Será que todos os bytes enviados estão realmente guardadas? Será que conseguimos verificar?
    #Veja o que faz a funcao do enlaceRX  getBufferLen
    progress['value'] = 60
    root.update_idletasks()
    
    
    
    #acesso aos bytes recebidos
    rxBuffer, nRx = com_volta.getData(tamanho)
    
    progress['value'] = 80
    root.update_idletasks()
    
    com_volta.sendData(data)
    
    print("COMPARANDO ARQUIVOS...")
    if tamanho_recebido == tamanho:
        
        print("-------------------------")
        print("ARQUIVOS IGUAIS!")

        imageW = "downloadArduino.png"
        #arquivo chegou inteiro!
        print("-------------------------")
        print("SALVANDO...")

        f = open(imageW, "wb")
        f.write(rxBuffer)
        
        progress['value'] = 90
        root.update_idletasks()
        
        f.close()
    
        # Encerra comunicaçãos
        print("-------------------------")
        print("COMUNICAÇÃO ENCERRADA!")
        print("-------------------------")
        com_volta.disable()
        
        end = time.time()
        
        print("TAXA DE RECEBIMENTO DE BITS: {0} Mb/s".format((tamanho/1000*1000)/(end-start)))
        print("-------------------------")
        
        progress['value'] = 100
        root.update_idletasks()
    
    else:
        print("-------------------------")
        print("BITS PERDIDOS!")
        com_volta.disable()
            
        
    
    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
proc = Button(root, text = 'Get Data', command = lambda: main_volta()) 
proc.pack() 

root.title("Client - Server")

proc.place(relx = 0.2, x =20, y = 50, anchor = NE)

progress.pack(pady =50)

mainloop()