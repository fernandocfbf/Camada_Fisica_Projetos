#####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 


from enlace import *
import time


# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM5"                  # Windows(variacao de)


def main():
    try:
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com = enlace(serialName)
    
        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com.enable()
    
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        print("Comunicação estabelecida com sucesso!!")
        
        #aqui você deverá gerar os dados a serem transmitidos. 
        #seus dados a serem transmitidos são uma lista de bytes a serem transmitidos. Gere esta lista com o 
        #nome de txBuffer. Esla sempre irá armazenar os dados a serem enviados.
        imageR = "download.png"
        imageW = "downloadArduino.png"
        
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
        
        print("Tamanho do txSize: {0} e {1}".format(txSize, len(txBuffer)))
       
        #Agora vamos iniciar a recepção dos dados. Se algo chegou ao RX, deve estar automaticamente guardado
        #Observe o que faz a rotina dentro do thread RX
        #print um aviso de que a recepção vai começar.
        print("Início da recepção de dados...")
        
        #Será que todos os bytes enviados estão realmente guardadas? Será que conseguimos verificar?
        #Veja o que faz a funcao do enlaceRX  getBufferLen
        
        #txLen = len(txBuffer)
        
        #acesso aos bytes recebidos
        rxBuffer, nRx = com.getData(txSize)
        print(rxBuffer)
    
        print("Salvando dados no arquivo")
        print(" - {}".format(imageW))
        f = open(imageW, "wb")
        f.write(rxBuffer)
        
        print (rxBuffer)
        
        f.close()
    
        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com.disable()
    except:
        print("ops! :-\\")
        com.disable()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
