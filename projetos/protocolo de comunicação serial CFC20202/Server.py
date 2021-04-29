#####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação
####################################################


## Estou fazendo a parte de recepção do server, na parte que da erro de recepção

from enlace import *
import time
from tkinter import *
from tkinter.ttk import *
import re
from tqdm.auto import tqdm
from tkinter import Label
from tkinter.filedialog import askopenfile
import libscrc
from datetime import datetime

serialName = "COM3"                  # Windows(variacao de)

root = Tk() 
root.geometry('400x150') 

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
    
def recebe_pacote(porta):
    
    #identifica o header
    header, nRx = porta.getData(10)
    
    #cria o idenitificador de pacotes
    indentificador = int(header[0])
    
    #cria o id do sensor em bytes
    id_sensor = int(header[1])
    
    #cria o id do servidor em bytes
    id_servidor = int(header[2])
    
    #transforma a quantidade de pacotes em bytes
    qtd_pacotes = int(header[3])
    
    #transforma o número do pacote atual em byte
    numero_do_pacote = int(header[4])
    
    #cria o numero do pacote de recomeço em bytes
    numero_do_pacote_de_recomeço = int(header[6])
    
    #cria o numero do ultimo pacote recebido com sucesso
    ultimo = int(header[7])
    
    #cria o tamanho do payload em bytes
    tamanho_do_payload = int(header[5])
    
    #crc do pacote 
    crc = int.from_bytes(header[8:10], byteorder='big')
    
    time.sleep(0.5)
    
    #pega o pacote completo
    pacote_completo, tamanho_do_p = porta.getData(tamanho_do_payload + 4)
    
    #pega somente payload 
    payload = pacote_completo[0: len(pacote_completo) - 4]
    
    #pega somente o EOP
    EOP = pacote_completo[len(pacote_completo) - 4 : len(pacote_completo)]
    
    return indentificador, id_sensor, id_servidor, qtd_pacotes, numero_do_pacote, tamanho_do_payload, numero_do_pacote_de_recomeço, ultimo, payload, EOP, crc
    
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
    
def fabrica(indentificador, id_sensor, id_servidor, qtd_pacotes, numero_do_pacote, id_arquivo, numero_do_pacote_de_recomeço, ultimo, payload):
    
    #cria o idenitificador de pacotes
    indentificador_bytes = int(indentificador).to_bytes(1, byteorder='big')
    
    #cria o id do sensor em bytes
    id_sensor_bytes = int(id_sensor).to_bytes(1, byteorder='big')
    
    #cria o id do servidor em bytes
    id_servidor_bytes = int(id_servidor).to_bytes(1, byteorder='big')
    
    #transforma a quantidade de pacotes em bytes
    qtd_pacotes_bytes = int(qtd_pacotes).to_bytes(1, byteorder='big')
    
    #transforma o número do pacote atual em byte
    numero_do_pacote_bytes = int(numero_do_pacote).to_bytes(1, byteorder='big')
    
    #cria o numero do pacote de recomeço em bytes
    numero_do_pacote_de_recomeço_bytes = int(numero_do_pacote_de_recomeço).to_bytes(1, byteorder='big')
    
    #cria o numero do ultimo pacote recebido com sucesso
    ultimo_bytes = int(ultimo).to_bytes(1, byteorder='big')
    
    #tamanho do payload 
    tamanho_payload_bytes = int(len(payload)).to_bytes(1, byteorder='big')
    
    #faz um complemento 
    complemento = int(0).to_bytes(2, byteorder='big')
    
    #cria o head, onde os 7 primeiros bytes são o numero de pacotes e os 3 ultimos o número do pacote 
    head = indentificador_bytes + id_sensor_bytes + id_servidor_bytes + qtd_pacotes_bytes + numero_do_pacote_bytes + tamanho_payload_bytes + numero_do_pacote_de_recomeço_bytes + ultimo_bytes + complemento
    
    #define o final do pacote
    EOP = int(0).to_bytes(4, byteorder='big')
    
    #monta o pacote completo
    pacote_completo = head + payload + EOP
    
    return pacote_completo

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

def ping(porta_com, id_do_servidor, arquivo):
    
    print("Servidor ativado")
    arquivo.write("Servidor ativado \n")
    
    #enquanto não chega nada, fica em looping infinito
    while porta_com.rx.getIsEmpty() == True:
        pass
    
    print("recebendo pacote...")
    arquivo.write("recebendo pacote... \n")
    #tempo para chegar todo o pacote
    time.sleep(1)
    
    #le os dados que estão chegando
    indentificador, id_sensor, id_servidor, qtd_pacotes, numero_do_pacote, tamanho_do_payload, numero_do_pacote_de_recomeço, ultimo, payload, EOP, crc = recebe_pacote(porta_com)

    #se o conteudo for igual ao pacote de teste combinado...
    if str(indentificador) == "1" and id_servidor == id_do_servidor:
        
        print("pacote de teste indentificado, enviando resposta...")
        arquivo.write("pacote de teste indentificado, enviando resposta... \n")
        
        pacote_resposta = fabrica(2, id_sensor, id_servidor, 0, 0, 0, 0, 0, bytes())
        
        #pacote de teste recebido
        porta_com.sendData(pacote_resposta)
        
        #esvazia o buffer
        porta_com.rx.clearBuffer()
    
    
    else:
        
        #esvazia o buffer
        porta_com.rx.clearBuffer()
        
        print("pacote recebido não identificado!")
        arquivo.write("pacote recebido não identificado! \n")

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

def recebendo(porta_com, id_sensor, id_servidor, arquivo):
    
    #variavel que determina o fim da recepcao
    concluido = False
    
    #variavel que armazena o arquivo completo
    arquivo_completo = bytes()
    
    #cria o numero do primeiro pacote
    pacote_anterior = 0
    
    print("")
    arquivo.write(" \n")
    print("------------ INICIANDO RECEPÇÃO ------------")
    arquivo.write("------------ INICIANDO RECEPÇÃO ------------ \n")
    
    while concluido == False:
        
        #extrai todas as informações do header, payload e EOP
        indentificador, id_sensor, id_servidor, qtd_pacotes, numero_do_pacote, tamanho_do_payload, numero_do_pacote_de_recomeço, ultimo, payload, EOP, crc = recebe_pacote(porta_com)
        
        #cria o crc
        crc_para_verificar = extrai_crc(payload)
        
        #cria o horário de agora para adicionar no print do arquivo
        now = datetime.now()
        
        #cria variavel de verificação de EOP
        verifica_EOP = False
        
        #cria variavel de verificação de numero de pacote
        verifica_pacote = False
        
        #cria variavel de verificação de tamanho do payload
        verifica_paylaod = False
        
        #verifica se o crc chegou certo
        verifica_crc = False
        
        if crc == crc_para_verificar:
            verifica_crc = True
        
        if int.from_bytes(EOP, "big") == 0:
            verifica_EOP = True
            
        if numero_do_pacote == pacote_anterior + 1:
            verifica_pacote = True
        
        if tamanho_do_payload <= 114:
            verifica_paylaod = True
            

        #se estiver tudo certo...
        if verifica_pacote == True and verifica_EOP == True and verifica_paylaod == True and verifica_crc == True:
            
            #fabrica o pacote de devolucao
            pacote_devolucao = fabrica(4, id_sensor, id_servidor, qtd_pacotes, numero_do_pacote, 1, numero_do_pacote_de_recomeço, pacote_anterior, payload)
            
            #envia a reposta
            porta_com.sendData(pacote_devolucao)
            
            print("MOMENTO: {0} | PACOTE {1} | STATUS: 4 | PAYLOAD: {2} | PACOTES: {3} | CRC: {4}".format(now, numero_do_pacote, len(payload), qtd_pacotes, crc_para_verificar))
            
            a = "MOMENTO: {0} | PACOTE {1} | STATUS: 4 | PAYLOAD: {2} | PACOTES: {3} | CRC: {4} \n".format(now, numero_do_pacote, len(payload), qtd_pacotes, crc_para_verificar)
            
            arquivo.write(a)
            
            
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
            pacote_devolucao = fabrica(6, id_sensor, id_servidor, qtd_pacotes, numero_do_pacote, 1, numero_do_pacote, pacote_anterior, payload)

            #envia a reposta
            porta_com.sendData(pacote_devolucao)
            
            print("MOMENTO: {0} | PACOTE {1} | STATUS: 6 | PAYLOAD: {2} | PACOTES: {3} | CRC: {4}".format(now, pacote_anterior+1, len(payload), qtd_pacotes, crc_para_verificar))
            
            a = "MOMENTO: {0} | PACOTE {1} | STATUS: 6 | PAYLOAD: {2} | PACOTES: {3} | CRC: {4} \n".format(now, pacote_anterior+1, len(payload), qtd_pacotes, crc_para_verificar)
            
            arquivo.write(a)
    
    return arquivo_completo
    

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
    
def extrai_crc(payload):
    crc = libscrc.modbus(payload)
    return crc

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------


def run():

    try:
    
        arquivo = open("Server4.txt", "a")
        
        id_sensor = 1
        id_servidor = 2
        
        #cria porta de comunicação
        com = enlace(serialName)
        
        #ativa porta de comunicação
        com.enable()
        
        print("-------- TESTANDO COMUNICAÇÃO --------")
        arquivo.write("-------- TESTANDO COMUNICAÇÃO -------- \n")
        ping(com, id_servidor, arquivo)
        
        print("--------------------------------------")
        arquivo.write("-------------------------------------- \n")
        #recebe o arquivo
        arquivo_ = recebendo(com, id_sensor, id_servidor, arquivo)
        
        #caminho da imagem que será salva 
        imageW = "downloadArduino.png"
        
    
        #salva a imagem lida -------
        f = open(imageW, "wb")
        f.write(arquivo_)
        f.close()
        #---------------------------
        print("--------------------------------------")
        arquivo.write("-------------------------------------- \n")
        print("")
        arquivo.write("")
        print("------- ENCERRANDO COMUNICAÇÃO -------")
        arquivo.write("------- ENCERRANDO COMUNICAÇÃO ------- \n")
        
    #        #fabrica pacote de encerramento
    #        pacote_de_encerramento = fabrica_comunicacao(1, 0, com, 0, bytes())
    #        
    #        #envia pacote de encerramento
    #        com.sendData(pacote_de_encerramento)
    #        
        #desabilita porta de comunicação
        com.disable()
        print("Comunicação encerrada!")
        arquivo.write("Comunicação encerrada! \n") 
        print("")
        arquivo.write(" \n")
        print("--------------- STATUS ---------------")
        arquivo.write("--------------- STATUS --------------- \n")
        print("Comunicação realizada com sucesso!")
        arquivo.write("Comunicação realizada com sucesso! \n")
    
    
    except:
        
         print("ops! :-\\")
         com.disable()
        
proc = Button(root, text = 'Get Data', command = lambda: run()) 
proc.pack()

root.title("HandShake")

proc.place(relx = 0.2, x =150, y = 50, anchor = NE)

mainloop()