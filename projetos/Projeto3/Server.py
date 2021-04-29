#####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação
####################################################

from enlace import *
import time
from tkinter import *
from tkinter.ttk import *
import re
from tqdm.auto import tqdm
from tkinter import Label
from tkinter.filedialog import askopenfile


serialName = "COM3"                  # Windows(variacao de)

root = Tk() 
root.geometry('400x150') 

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
    
def recebe_pacote(porta):
    
    #identifica o header
    header, nRx = porta.getData(10)
    
    #identifica o numero de pacotes
    qtd_pacotes = int.from_bytes(header[0:4], "big")
    
    #identifica o numero do pacote atual
    numero_do_pacote = int.from_bytes(header[4:8], "big")
    
    #identifica o tamanho do payload
    tamanho_do_payload = int(header[8])
    
    #identifica o tipo de pacote
    identificador = int(header[9])
    
    time.sleep(0.5)
    
    #pega o pacote completo
    pacote_completo, tamanho_do_p = porta.getData(tamanho_do_payload + 4)
    
    #pega somente payload 
    payload = pacote_completo[0: len(pacote_completo) - 4]
    
    #pega somente o EOP
    EOP = pacote_completo[len(pacote_completo) - 4 : len(pacote_completo)]
    
    return qtd_pacotes, numero_do_pacote, tamanho_do_payload, identificador, payload, EOP
    
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
    
def fabrica(tipo, numero_do_pacote, porta_com, qtd_pacotes, payload):
    
    #indentifica o tamanho do payload
    tamanho_do_payload = len(payload).to_bytes(1, byteorder='big')
    
    #transforma a quantidade de pacotes em bytes
    qtd_pacotes_bytes = int(qtd_pacotes).to_bytes(4, byteorder='big')
    
    #transforma o número do pacote atual em byte
    numero_do_pacote_bytes = int(numero_do_pacote).to_bytes(4, byteorder='big')
    
    #cria o idenitificador de pacotes
    if tipo == "teste":
        identificador = int(0).to_bytes(1, byteorder='big')
    else:
        identificador = int(1).to_bytes(1, byteorder='big')
    
    #cria o head, onde os 7 primeiros bytes são o numero de pacotes e os 3 ultimos o número do pacote 
    head = qtd_pacotes_bytes + numero_do_pacote_bytes + tamanho_do_payload + identificador
    
    #define o final do pacote
    EOP = int(0).to_bytes(4, byteorder='big')
    
    #monta o pacote completo
    pacote_completo = head + payload + EOP
    
    return pacote_completo

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

def ping(porta_com):
    
    print("Servidor ativado")
    
    #enquanto não chega nada, fica em looping infinito
    while porta_com.rx.getIsEmpty() == True:
        pass
    
    print("recebendo pacote...")
    #tempo para chegar todo o pacote
    time.sleep(1)
    
    #le os dados que estão chegando
    qtd_pacotes, numero_do_pacote, tamanho_do_payload, identificador, payload, EOP = recebe_pacote(porta_com)

    #se o conteudo for igual ao pacote de teste combinado...
    if str(identificador) == "0":
        
        print("pacote de teste indentificado, enviando resposta...")
        
        pacote_resposta = fabrica("teste", 0, porta_com, 0, bytes())
        
        #pacote de teste recebido
        porta_com.sendData(pacote_resposta)
        
        #esvazia o buffer
        porta_com.rx.clearBuffer()
    
    
    else:
        
        #esvazia o buffer
        porta_com.rx.clearBuffer()
        
        print("pacote recebido não identificado!")

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
        
def fabrica_comunicacao(confirma_chegada, numero_do_pacote, porta_com, qtd_pacotes, payload):
    
    #transforma a quantidade de pacotes em bytes
    qtd_pacotes_bytes = int(qtd_pacotes).to_bytes(4, byteorder='big')
    
    #transforma o número do pacote atual em byte
    numero_do_pacote_bytes = int(numero_do_pacote).to_bytes(4, byteorder='big')
    
    #cria o idenitificador de pacotes
    if confirma_chegada == 0:
        confirma_chegada = int(0).to_bytes(1, byteorder='big')
    else:
        confirma_chegada = int(1).to_bytes(1, byteorder='big')
        
    #indeintifica tamanho do payload
    tamanho_do_payload = len(payload).to_bytes(1, byteorder='big')
    
    #cria o head, onde os 7 primeiros bytes são o numero de pacotes e os 3 ultimos o número do pacote 
    head = qtd_pacotes_bytes + numero_do_pacote_bytes + tamanho_do_payload + confirma_chegada
    
    #define o final do pacote
    EOP = int(0).to_bytes(4, byteorder='big')
    
    #monta o pacote completo
    pacote_completo = head + EOP
    
    return pacote_completo
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

def recebendo(porta_com):
    
    #variavel que determina o fim da recepcao
    concluido = False
    
    #variavel que armazena o arquivo completo
    arquivo_completo = bytes()
    
    #cria o numero do primeiro pacote
    pacote_anterior = 0
    
    print("")
    print("------------ INICIANDO RECEPÇÃO ------------")
    
    while concluido == False:
        
        #extrai todas as informações do header, payload e EOP
        qtd_pacotes, numero_do_pacote, tamanho_do_payload, identificador, payload, EOP = recebe_pacote(porta_com)
        
        #cria variavel de verificação de EOP
        verifica_EOP = False
        
        #cria variavel de verificação de numero de pacote
        verifica_pacote = False
        
        #cria variavel de verificação de tamanho do payload
        verifica_paylaod = False
        
        if int.from_bytes(EOP, "big") == 0:
            verifica_EOP = True
            
        if numero_do_pacote == pacote_anterior + 1:
            verifica_pacote = True
        
        if tamanho_do_payload <= 114:
            verifica_paylaod = True
            

        #se estiver tudo certo...
        if verifica_pacote == True and verifica_EOP == True and verifica_paylaod == True:
            
            #fabrica o pacote de devolucao
            pacote_devolucao = fabrica_comunicacao(1, numero_do_pacote, porta_com, qtd_pacotes, payload)
            
            #envia a reposta
            porta_com.sendData(pacote_devolucao)
            
            print("PACOTE {0} | STATUS: confirmado | RESPOSTA: enviada".format(numero_do_pacote))
                
            #atualiza o numero do pacote
            pacote_anterior = numero_do_pacote
            
            #soma o payload no arquivo
            arquivo_completo += payload
            
            #verifica se é o último pacote
            if numero_do_pacote == qtd_pacotes:
                concluido = True
                
        #se algo chegou errado...            
        else:
            
            #fabrica o pacote de devolucao
            pacote_devolucao = fabrica_comunicacao(0, pacote_anterior + 1, porta_com, qtd_pacotes, payload)

            #envia a reposta
            porta_com.sendData(pacote_devolucao)
            
            print("PACOTE {0} | STATUS: erro | RESPOSTA: enviada".format(pacote_anterior + 1))
            
    
    return arquivo_completo
    

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

def run():

    try:
        #cria porta de comunicação
        com = enlace(serialName)
        
        #ativa porta de comunicação
        com.enable()
        
        print("-------- TESTANDO COMUNICAÇÃO --------")
        ping(com)
        print("--------------------------------------")
        
        #recebe o arquivo
        arquivo = recebendo(com)
        
        #caminho da imagem que será salva 
        imageW = "downloadArduino.png"
        
    
        #salva a imagem lida -------
        f = open(imageW, "wb")
        f.write(arquivo)
        f.close()
        #---------------------------
        print("--------------------------------------")
        print("")
        print("------- ENCERRANDO COMUNICAÇÃO -------")
        
        #fabrica pacote de encerramento
        pacote_de_encerramento = fabrica_comunicacao(1, 0, com, 0, bytes())
        
        #envia pacote de encerramento
        com.sendData(pacote_de_encerramento)
        
        #desabilita porta de comunicação
        com.disable()
        print("Comunicação encerrada!")
        print("")
        print("--------------- STATUS ---------------")
        print("Comunicação realizada com sucesso!")
        
    
    except:
        
         print("ops! :-\\")
         com.disable()
        
proc = Button(root, text = 'Get Data', command = lambda: run()) 
proc.pack()

root.title("HandShake")

proc.place(relx = 0.2, x =150, y = 50, anchor = NE)

mainloop()