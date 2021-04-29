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

def ping(porta_com, pacote):
    
    #cria uma verificação de ping
    ping_concluido = False

    #salva a primeira tentativa
    tentativa = 0
    
    testa = "y"
    
    while porta_com.rx.getIsEmpty() == True:
        
        #se não for a primeira tentativa pergunta se gostaria de tentar de novo
        if tentativa != 0:
            print("O servidor não está respondendo")
            #pergunta se quer testar comunicação
            testa = input("Você gostaria de testar a comunicação novamente? [y,n] ")
        
        
        #se quiser testar...
        
        if testa == "y" or tentativa == 0:
            print("Enviando handShake...")
            
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
            print("--------------------------------------")
            print(" ")
            porta_com.disable()
            break
    
    if porta_com.rx.getIsEmpty() == False:
        
        #identifica tipo de pacote
        ident = recebe_pacote(porta_com)
        
        if ident == 0:
            
            print("Comunicação estabelecida!")
            print("--------------------------------------")
            print(" ")
        
        else:
            
            print("Protocolo corrompido")
            print("--------------------------------------")
            print(" ")
            porta_com.disable()
            
        
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

def recebe_pacote_de_confirmacao(porta):

    #identifica o header
    header, nRx = porta.getData(10)

    #identifica o numero de pacotes
    qtd_pacotes = int.from_bytes(header[0:4], "big")
    
    #identifica o numero do pacote atual
    numero_do_pacote = int.from_bytes(header[4:8], "big")
    
    #tamanho do payload enviado
    tamanho = int(header[8])
    
    #identifica o tamanho do payload
    confirma_chegada = int(header[9])
    
    time.sleep(0.5)
    
    #pega o pacote completo
    pacote_completo, tamanho_do_p = porta.getData(4)
    
    #pega somente o EOP
    EOP = pacote_completo[len(pacote_completo) - 4 : len(pacote_completo)]
    
    return qtd_pacotes, numero_do_pacote, confirma_chegada, EOP, tamanho
        
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
    
def envia_arquivo(lista_de_payloads, porta_com):
    
    #número de pacotes:
    qtd_pacotes = len(lista_de_payloads)
    
    #cria contador
    indice = 0
    
    while indice < len(lista_de_payloads):
        
        

        porta_com.rx.clearBuffer()
        
        #pega o payload
        payload = lista_de_payloads[indice]
        
        #tipo do pacote
        tipo = "comunicação"
        
        if indice == 5:
            #fabrica um pacote
            pacote = fabrica(tipo, indice+1, porta_com, qtd_pacotes, payload+payload)
        
        else:
            #fabrica um pacote
            pacote = fabrica(tipo, indice+1, porta_com, qtd_pacotes, payload)
        
        porta_com.sendData(pacote)
        
        time.sleep(1)
        
        #faz leitura do pacote
        qtd_pacotes_c, numero_do_pacote_c, confirma_chegada_c, EOP_c, tamanho_c = recebe_pacote_de_confirmacao(porta_com)
        
        
        if qtd_pacotes == qtd_pacotes_c and numero_do_pacote_c == indice+1 and confirma_chegada_c == 1 and len(payload) == tamanho_c:
            
            print("PACOTE {0} | STATUS: confirmado".format(numero_do_pacote_c))
            
            indice += 1
        
        else:
            
            print("PACOTE {0} | STATUS: erro".format(numero_do_pacote_c))
        
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
            
def recebe_pacote(porta):
    #identifica o header
    header, nRx = porta.getData(10)
    
    #identifica o tamanho do payload
    tamanho_do_payload = int(header[8])
    
    #identifica o tipo de pacote
    identificador = int(header[9])
    
    time.sleep(0.5)
    
    #pega o pacote completo
    pacote_completo, tamanho_do_p = porta.getData(tamanho_do_payload + 4)
    
    return identificador

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
    
def run():
    
    try:

        # cria porta de comunicação
        com = enlace(serialName)
    
        #ativa porta de comunicação
        com.enable()
        
        print("-------- TESTANDO COMUNICAÇÃO --------")
        
        #payload de teste
        payload_teste = int(4).to_bytes(1, byteorder='big')
        
        #cria um pacote teste
        pacote_teste = fabrica("teste", 1, com, 1, payload_teste)
        
        #pinga o servidor
        ping(com, pacote_teste)
        
        #imagem para ser lida
        imageR = str(file_name)
        
        #abre a imagem e le
        txBuffer = open(imageR, "rb").read()
        
        #segmenta o arquivo em pacotes
        a = segmentador(txBuffer)
        
        print("------ INICIANDO ENVIO DE DADOS ------")
        
        #envia o arquivo para o server
        envia_arquivo(a, com)
        
        com.rx.clearBuffer()
        
        print("--------------------------------------")
        print("")
        print("------- ENCERRANDO COMUNICAÇÃO -------")
        #desalbilita a porta de comunicação
        com.disable()
        print("Comunicação encerrada!")
        print("")
        print("--------------- STATUS ---------------")
        
        print("Comunicação realizada com sucesso!")
        
        
            
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