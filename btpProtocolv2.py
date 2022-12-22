import os                                                                   # importando o módulo de Sistemas Operacionais
import threading                                                            # importando o módulo de Theads

semaphore = threading.Semaphore(1)                                          # criando Semáforo que será utilizado na função "ADD" do server

def processing(message, connection, client):
    message = message.decode()
    print(f'Cliente {client} enviou {message}')
    message = message.split()

    if message[0].upper() == 'GET':                                         # comando DOWN (baixa o arquivo)
        fileName = ' '.join(message[1:])
        print(f'Arquivo solicitado: {fileName}')
        try:                                                                # envio do tamanho do arquivo
            fileStatus = os.stat(fileName)
            connection.send(str.encode(f'+OK {fileStatus.st_size}\n'))

            file = open(fileName, 'rb')                                     # envio do arquivo

            while (True):
                data = file.read(1024)
                if not data:
                    break
                connection.send(data)
        except Exception as error:
            connection.send(str.encode(f'-ERR {error}\n'))
    elif (message[0].upper() == 'CWD'):                                     # comando CD (muda de diretório)
        try:
            os.chdir(message[1])
            connection.send(str.encode(f'+OK\n'))                           # caso o diretório exista, o path será alterado e o servidor devolverá uma mensagem de status
        except:
            connection.send(str.encode(f'-ERR Diretório não existente!\n')) # mensagem de erro que será emitida caso o diretório desejado não exista
    elif (message[0].upper() == 'LIST'):                                    # comando LS (lista os arquivos/diretórios)
        listFiles = os.listdir('.')                                         # retorna uma lista contendo o nome dos diretórios
        connection.send(str.encode(f'+OK {len(listFiles)}\n'))

        for fileName in listFiles:                                          # verifica se é arquivo e printa-o
            if os.path.isfile(fileName):
                fileStatus = os.stat(fileName)                              # retorna o tamanho do arquivo
                connection.send(str.encode(f'Arquivo: {fileName} - {fileStatus.st_size/1024}KB\n'))
            elif os.path.isdir(fileName):                                   # verifica se é diretório e printa-o
                connection.send(str.encode(f'Diretório: {fileName}\n'))
            else:
                connection.send(str.encode(f'Outros: {fileName}\n'))        # para o caso de outros 
    elif (message[0].upper() == 'ADD'):                                     # comando UP (cria um arquivo e o hospeda no servidor)
        semaphore.acquire()                                                 # inicializa o semáforo
        fileName = ' '.join(message[1:])
        connection.send(str.encode(f'+OK\n'))
        with open(fileName, 'ab') as file:
            while (True):
                data = connection.recv(1024)
                if (data.decode() == 'end'):
                    break
                file.write(data)
                file.write(str.encode('\n'))
        semaphore.release()                                                 # libera o semáforo
    elif (message[0].upper() == 'READ'):                                    # comando CAT (visualiza o conteúdo do arquivo)
        fileName = ' '.join(message[1:])
        print(f'Arquivo solicitado: {fileName}')

        try:
            fileStatus = os.stat(fileName)
            connection.send(str.encode(f'+OK {fileStatus.st_size}\n'))

            file = open(fileName, 'rb')                                     # envio do arquivo
            while (True):
                data = file.read(1024)
                if not data:
                    break
                connection.send(data)
        
        except Exception as error:
            connection.send(str.encod(f'-ERR {error}\n'))                   # mensagem de erro

    elif (message[0].upper() == 'MKDIR'):                                   # comando CRDIR (cria um diretório no servidor)
        try:
            os.mkdir('./' + message[1])
            connection.send(str.encode(f'+OK\n'))
        except:                                                             # mensagem de erro para o caso de já existir um diretório com o mesmo nome
            connection.send(str.encode(f'-ERR Diretório já existente\n'))
    elif (message[0].upper() == 'QUIT'):                                    # comando EXIT (encerra a conexão com o servidor)
        connection.send(str.encode(f'+OK\n'))
        return False
    else:                                                                   # caso o comando digitado não esteja no dicionário
        connection.send(str.encode(f'-ERR Comando inválido!\n')) 
    
    return True