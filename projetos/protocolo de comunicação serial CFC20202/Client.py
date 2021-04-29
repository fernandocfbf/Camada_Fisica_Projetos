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
import libscrc
from datetime import datetime

#   python -m serial.tools.list_ports

#porta de comunicação
serialName = "COM5" 

root = Tk() 
root.geometry('400x150') 
file_text = Text(root, height=0.5, width=22)

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

def open_file(): 
    global file_name
    file = askopenfile(mode ='r', filetypes =[("Image File",'.png')]) 
    if file is not None: 
        file_name = file.name
        file_text.insert(END, file_name)
        print(file_name)
        
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

def ping(porta_com, pacote, arquivo):
    
    #cria uma verificação de ping
    ping_concluido = False

    #salva a primeira tentativa
    tentativa = 0
    
    testa = "y"
    
    resposta = True
    
    while porta_com.rx.getIsEmpty() == True:
        
        #se não for a primeira tentativa pergunta se gostaria de tentar de novo
        if tentativa != 0:
            
            print("O servidor não está respondendo")
            arquivo.write("O servidor não está respondendo \n")
            
            #pergunta se quer testar comunicação
            testa = input("Você gostaria de testar a comunicação novamente? [y,n] ")
            arquivo.write("Você gostaria de testar a comunicação novamente? [y,n] \n")
        
        
        #se quiser testar...
        if testa == "y" or tentativa == 0:
            print("Enviando handShake...")
            arquivo.write("Enviando handShake... \n")
            
            #envia novo pacote
            porta_com.sendData(pacote)
            
            #não será mais uma tentativa
            tentativa += 1
            
            #tempo de espera do client
            tempo_em_segundos = 0
    
            #enquanto não receber resposta e o tempo for menor que 5 seg...
            while ping_concluido == False and tempo_em_segundos < 5:
                
                #se a porta não receber retorno...
                if porta_com.rx.getIsEmpty() == True:
                    
                    #espera mais algum tempo
                    tempo_em_segundos += 1
                    time.sleep(1)
                
                #caso receba retorno sai do while
                else:
                    ping_concluido = True
        
        #se não quiser testar...
        else:
            print("Comunicação encerrada")
            arquivo.write("Comunicação encerrada \n")
            print("--------------------------------------")
            arquivo.write("-------------------------------------- \n")
            print(" ")
            arquivo.write(" \n")
                    
            resposta = False
            porta_com.disable()
            break
            
    
    if porta_com.rx.getIsEmpty() == False:
        
        #identifica tipo de pacote
        indentificador, id_sensor, id_servidor, qtd_pacotes, numero_do_pacote, id_arquivo, numero_do_pacote_de_recomeço, ultimo, payload, EOP = recebe_pacote(porta_com)
        
        if indentificador == 2:
            
            print("Comunicação estabelecida!")
            arquivo.write("Comunicação estabelecida! \n")
            print("--------------------------------------")
            arquivo.write("-------------------------------------- \n")
            print(" ")
            arquivo.write(" \n")
        
        else:
            
            print("Protocolo corrompido")
            arquivo.write("Protocolo corrompido \n")
            print("--------------------------------------")
            arquivo.write("-------------------------------------- \n")
            print(" ")
            arquivo.write(" \n")
            porta_com.disable()
            
    return resposta
        
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
        
def fabrica(indentificador, id_sensor, id_servidor, qtd_pacotes, numero_do_pacote, id_arquivo, numero_do_pacote_de_recomeço, ultimo, payload, crc):
    
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
    
    #faz um complemento 
    complemento = int(crc).to_bytes(2, byteorder='big')
    
    #cria o tamanho do payload em bytes
    tamanho_payload_bytes = int(len(payload)).to_bytes(1, byteorder='big')
    
    #cria o head, onde os 7 primeiros bytes são o numero de pacotes e os 3 ultimos o número do pacote 
    head = indentificador_bytes +  id_sensor_bytes + id_servidor_bytes + qtd_pacotes_bytes + numero_do_pacote_bytes + tamanho_payload_bytes + numero_do_pacote_de_recomeço_bytes + ultimo_bytes + complemento
    
    #define o final do pacote
    EOP = int(0).to_bytes(4, byteorder='big')
    
    #monta o pacote completo
    pacote_completo = head + payload + EOP
    
    return pacote_completo

        
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

def segmentador(arquivo):
    
    #define o tamanho do arquivo
    tamanho_do_arquivo = len(arquivo)
    
    #verifica se só um pacote dá conta...
    if tamanho_do_arquivo < 114:
        numero_de_pacotes = 1
    
    #se o tamanho for multiplo...
    elif tamanho_do_arquivo%114 == 0:
        
        #define o número de pacotes
        numero_de_pacotes = tamanho_do_arquivo/114
    
    #se não for multiplo temos que arredondar para cima
    else:
        
        #define o numero de pacotes
        numero_de_pacotes = int(tamanho_do_arquivo/114) + 1
    
    #cria uma lista que separará o arquivo em segmentos para serem usados como
    #payload
    lista_payloads = list()
    
    #numeros que serão atualizados a cada iteração para segregar os pacotes
    comeco_do_pacote = 0
    fim_do_pacote = 114
    
    #define se acabamos de segregar ou não
    pacote_atual = 0
    
    #enquanto não forem produzidos todos os payloads...
    while pacote_atual < numero_de_pacotes:
        
        #cria novo payload
        payload = arquivo[comeco_do_pacote:fim_do_pacote]
    
        #adiciona na lista de payloads
        lista_payloads.append(payload)
        
        #atualiza o começo e fim
        comeco_do_pacote = fim_do_pacote
        fim_do_pacote += 114
        
        pacote_atual += 1
    
    return lista_payloads

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
    
    time.sleep(0.5)
    
    #pega o pacote completo
    pacote_completo, tamanho_do_p = porta.getData(tamanho_do_payload + 4)
    
    #pega somente payload 
    payload = pacote_completo[0: len(pacote_completo) - 4]
    
    #pega somente o EOP
    EOP = pacote_completo[len(pacote_completo) - 4 : len(pacote_completo)]
    
    return indentificador, id_sensor, id_servidor, qtd_pacotes, numero_do_pacote, tamanho_do_payload, numero_do_pacote_de_recomeço, ultimo, payload, EOP
    
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
    
def envia_arquivo(lista_de_payloads, porta_com, id_sensor, id_servidor, arquivo):
    
    deu = True
    
    #número de pacotes:
    qtd_pacotes = len(lista_de_payloads)
    
    #cria um id do arquivo
    id_arquivo = 12
    
    #cria contador
    indice = 0
    
    c = 0
    
    while indice < len(lista_de_payloads):
        
        #limpa o que recebeu
        porta_com.rx.clearBuffer()
        
        #pega o payload
        payload = lista_de_payloads[indice]
        
        #tipo do pacote
        tipo = 3
        
        #cria o crc
        crc = extrai_crc(payload)
        

        if indice == 5 and c == 5:
        
            #fabrica um pacote
            pacote = fabrica(tipo, id_sensor, id_servidor, qtd_pacotes, indice, id_arquivo, 0, indice+1, payload, crc)
        
        else:
            #fabrica um pacote
            print("aqui")
            pacote = fabrica(tipo, id_sensor, id_servidor, qtd_pacotes, indice+1, id_arquivo, 0, indice+1, payload, crc)
            
        #verifica se recebeu resposta dentro do tempo indicado
        resposta_recebida = porta_com.sendData_time(pacote, arquivo)
        
        #cria o horário de agora para adicionar no print do arquivo
        now = datetime.now()
        
        if resposta_recebida == True:
        
            #faz leitura do pacote
            indentificador_c, id_sensor_c, id_servidor_c, qtd_pacotes_c, numero_do_pacote_c, tamanho_payload_c, numero_do_pacote_de_recomeço_c, ultimo_c, payload_c, EOP_c = recebe_pacote(porta_com)
            
            if qtd_pacotes == qtd_pacotes_c and numero_do_pacote_c == indice+1 and indentificador_c == 4 and len(payload) == len(payload_c):
                
                print("MOMENTO: {0} | PACOTE {1} | STATUS: 4 | PAYLOAD: {2} | PACOTES: {3} | CRC: {4}".format(now, numero_do_pacote_c, len(payload), qtd_pacotes, crc))
                
                a = "MOMENTO: {0} | PACOTE {1} | STATUS: 4 | PAYLOAD: {2} | PACOTES: {3} | CRC: {4} \n".format(now, numero_do_pacote_c, len(payload), qtd_pacotes, crc)
                
                arquivo.write(a)
                        
                indice += 1
            
            else:
                
                indice = numero_do_pacote_de_recomeço_c
                print(indice)
                
                print("MOMENTO: {0} | PACOTE {1} | STATUS: 6 | PAYLOAD: {2} | PACOTES: {3} | CRC: {4}".format(now, numero_do_pacote_c+1, len(payload), qtd_pacotes, crc))
                
                a = "MOMENTO: {0} | PACOTE {1} | STATUS: 6 | PAYLOAD: {2} | PACOTES: {3} | CRC: {4} \n".format(now, numero_do_pacote_c+1, len(payload), qtd_pacotes, crc)
                
                c+=1 
                arquivo.write(a)
        
        else:
            indice = len(lista_de_payloads)
            print("Comunicação perdida!")
            arquivo.write("Comunicação perdida! \n")
            deu = False
            break
        
    return deu

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
            
def extrai_crc(payload):
    crc = libscrc.modbus(payload)
    return crc
            
    
    
def run():
    
    try:
        arquivo = open("Client4.txt", "a")
            
        id_sensor = 1
        id_servidor = 2
    
        # cria porta de comunicação
        com = enlace(serialName)
    
        #ativa porta de comunicação
        com.enable()
        
        print("-------- TESTANDO COMUNICAÇÃO --------")
        arquivo.write("-------- TESTANDO COMUNICAÇÃO -------- \n")
        
        #payload de teste
        payload_teste = int(4).to_bytes(1, byteorder='big')
        
        #cria um pacote teste
        pacote_teste = fabrica(1, id_sensor, id_servidor, 0, 0, 0, 0, 0, payload_teste, 0)
        
        #pinga o servidor
        resposta = ping(com, pacote_teste, arquivo)
        
        if resposta == True:
            
            #imagem para ser lida
            imageR = str(file_name)
            
            #abre a imagem e le
            txBuffer = open(imageR, "rb").read()
            
            #segmenta o arquivo em pacotes
            arquivo_segmentado = segmentador(txBuffer)
            
            print("------ INICIANDO ENVIO DE DADOS ------")
            arquivo.write("------ INICIANDO ENVIO DE DADOS ------ \n")
            
            #envia o arquivo para o server
            cop = envia_arquivo(arquivo_segmentado, com, id_sensor, id_servidor, arquivo)
            
            if cop == True:
                
                com.rx.clearBuffer()
                
                print("--------------------------------------")
                arquivo.write("-------------------------------------- \n")
                print("")
                arquivo.write(" \n")
                print("------- ENCERRANDO COMUNICAÇÃO -------")
                arquivo.write("------- ENCERRANDO COMUNICAÇÃO ------- \n")
                        
                        
                #desalbilita a porta de comunicação
                com.disable()
                print("Comunicação encerrada!")
                arquivo.write("Comunicação encerrada! \n")
                print("")
                arquivo.write(" \n")
                print("--------------- STATUS ---------------")
                arquivo.write("--------------- STATUS --------------- \n")
                print("Comunicação realizada com sucesso!")
                arquivo.write("Comunicação realizada com sucesso! \n")
                
            else:
                print("--------------------------------------")
                arquivo.write("-------------------------------------- \n")
                print("")
                arquivo.write(" \n")
                print("------- ENCERRANDO COMUNICAÇÃO -------")
                arquivo.write("------- ENCERRANDO COMUNICAÇÃO ------- \n")
                
                #desalbilita a porta de comunicação
                com.disable()
                print("Comunicação encerrada!")
                arquivo.write("Comunicação encerrada! \n")
                print("")
                arquivo.write(" \n")
                print("--------------- STATUS ---------------")
                arquivo.write("--------------- STATUS --------------- \n")
                print("Comunicação realizada perdida!")
                arquivo.write("Comunicação realizada perdida! \n")
                
        else:
            pass
        
    except:
        print("ops! :-\\")
        com.disable()

btn = Button(root, text ='Open', command = lambda:open_file()) 
btn.pack()     

proc = Button(root, text = 'Send Data', command = lambda: run()) 
proc.pack() 

root.title("Client - Server")

btn.place(relx = 0.2, x =20, y = 20, anchor = NE)
proc.place(relx = 0.2, x =150, y = 60, anchor = NE)

file_text.pack(pady = 22)

mainloop()