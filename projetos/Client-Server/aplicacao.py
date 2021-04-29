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
ida = "COM5"  
txSize = None                # Windows(variacao de)
imageW = None
com = None
txBuffer = None

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
        print("------------------------------------")
        
        print("ATIVANDO PORTA DE ENVIO")
        
        progress['value'] = 30
        root.update_idletasks()
    
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        
        #aqui você deverá gerar os dados a serem transmitidos. 
        #seus dados a serem transmitidos são uma lista de bytes a serem transmitidos. Gere esta lista com o 
        #nome de txBuffer. Esla sempre irá armazenar os dados a serem enviados.
        imageR = str(file_name)
        
        
        # <------------------------------------------------ IDA ------------------------------------------------------------>
        
        
        #txBuffer = bytes([255])
        txBuffer = open(imageR, "rb").read()
        progress['value'] = 60
        root.update_idletasks()
    
        #finalmente vamos transmitir os tados. Para isso usamos a funçao sendData que é um método da camada enlace.
        #faça um print para avisar que a transmissão vai começar.
        #tente entender como o método send funciona!
        
        #print("Início da Transmissão...")
        
        #manda o tamanho da informação
        tamanho_do_arquivo = (int(len(txBuffer))).to_bytes(2, byteorder='big')
        print(len(tamanho_do_arquivo))
        
        com.sendData(tamanho_do_arquivo)
        print("------------------------------------")
        print("ESTABELECENDO COMUNICAÇÃO PRÉVIA...")
        
        time.sleep(0.3)
        
        print("------------------------------------")
        print("TRANSFERINDO: {0} BYTES".format(len(txBuffer)))
        
        
        com.sendData(txBuffer)
        progress['value'] = 70
        root.update_idletasks()
        
        #time.sleep(2) #sem isso não da tempo de enviar a mensagem e por isso o txSize seria 0

        # A camada enlace possui uma camada inferior, TX possui um método para conhecermos o status da transmissão
        # Tente entender como esse método funciona e o que ele retorna
        txSize = int(com.tx.getStatus())
        
        progress['value'] = 90
        root.update_idletasks()
       
        #Agora vamos iniciar a recepção dos dados. Se algo chegou ao RX, deve estar automaticamente guardado
        #Observe o que faz a rotina dentro do thread RX
        #print um aviso de que a recepção vai começar.
        
        while True:
            if com.rx.getBufferLen() == 0:
                print("------------------------------------")
                print("ESPERANDO CONFIRMAÇÃO...")
                
                time.sleep(0.7)
                
            else:
                print("CONFIRMANDO...")
                data, n = com.getData(2)
                tamanho = int.from_bytes(data, "big")
                time.sleep(0.5)
                break
        
        if tamanho == len(txBuffer):
            print("------------------------------------")
            print("COMUNICAÇÃO CONFIRMADA!")
            
        else:
            print("------------------------------------")
            print("ALGO DEU ERRADO!")
                
        com.disable()
        print("------------------------------------")
        print("DESABILITANDO PORTA DE ENVIO")
        
        progress['value'] = 100
        root.update_idletasks()
        
    except:
        print("ops! :-\\")
        if com is not None:
            com.disable()
            

        
    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
btn = Button(root, text ='Open', command = lambda:open_file()) 
btn.pack()     

proc = Button(root, text = 'Send Data', command = lambda: main_ida()) 
proc.pack() 

root.title("Client - Server")

btn.place(relx = 0.2, x =20, y = 20, anchor = NE)
proc.place(relx = 0.2, x =20, y = 60, anchor = NE)

file_text.pack(pady = 22)
progress.pack(pady =0.15)

mainloop()
