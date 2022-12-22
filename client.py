import socket
import sys

MESSAGE_SIZE = 1024                                             # tamanho do bloco de mensagem
HOST = '127.0.0.1'                                              # ip da máquina que está rodando o servidor
PORT = 40000                                                    # porta que o servidor escuta

def decodeCommandUser(commandUser):
    commandList = {
        'down': 'get',                                          # faz download de um arquivo
        'cd': 'cwd',                                            # muda de diretório
        'ls': 'list',                                           # lista os arquivos em um diretório
        'up': 'add',                                            # faz upload de um arquivo
        'cat': 'read',                                          # mostra o conteúdo de um arquivo
        'crdir': 'mkdir',                                       # cria um diretório
        'exit': 'quit'                                          # encerra a conexão com o servidor
    }

    tokens = commandUser.split()
    if (tokens[0].lower()) in commandList:
        tokens[0] = commandList[tokens[0].lower()]
        return " ".join(tokens)
    else:
        return False

if (len(sys.argv) > 1):                                         # para se conectar ao ip da máquina que vai rodar o server
    HOST = sys.argv[1]

print(HOST)

print('-'*50)                                                   # menu
print('Servidor FTP - Projeto Final SO/PIRC')
print('-'*50)

print('O servidor possui as seguintes funções:\n\n- DOWN: Solicita o download de um arquivo\n- CD: Altera o diretório atual do servidor\n- LS: Solicita a lista de arquivos/diretórios\n- UP: Realiza o upload de um arquivo:\n- CAT: Exibe o conteúdo de um arquivo\n- CRDIR: Cria um novo diretório:\n- EXIT: Encerra a conexão com o servidor')
print('-'*50)

print('Dados do servidor:', HOST+':'+str(PORT))                 # impressão dos dados do servidor
server = (HOST, PORT)
serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # configuração do socket do cliente
serverSock.connect(server)                                      # estabelecimento da conexão ativa com o servidor                              

print('Para encerrar a conexão, use o comando "EXIT" ou pressione CTRL+C')

while (True):
    try:
        print('-'*50)
        commandUser = input('Comando >>> ')
    except:
        commandUser = 'EXIT'
    command = decodeCommandUser(commandUser)

    if not command:
        print('Comando "{}" não existe.'.format(commandUser))
    else:
        serverSock.send(str.encode(command))
        data = serverSock.recv(MESSAGE_SIZE)
        if not data:
            break
        messageStatus = data.decode().split('\n')[0]
        data = data[len(messageStatus)+1:]

        print(messageStatus)
        command = command.split()
        command[0] = command[0].upper()
        if (command[0] == 'QUIT'):                              # encerra a conexão com o servidor
            break
        elif (command[0] == 'GET'):                             # comando DOWN (baixa o arquivo)
            fileName = ' '.join(command[1:])
            fileSize = int(messageStatus.split()[1])
            print('Recebendo:', fileName)
            with open(fileName, 'wb') as file:
                while (True):
                    data = serverSock.recv(1024)
                    file.write(data)
                    fileSize -= len(data)
                    if (fileSize == 0):
                        break
        elif (command[0] == 'LIST'):                            # comando LS (lista os arquivos/diretórios)
            fileName = int(messageStatus.split()[1])
            data = data.decode()
            while (True):
                files = data.split('\n')
                residual = files[-1]      
                for file in files[:-1]:
                    print(file)
                    fileName -= 1
                if fileName == 0:
                    break
                data = serverSock.recv(MESSAGE_SIZE)
                if not data:
                    break
                data = residual + data.decode()
        elif (command[0].upper() == 'ADD'):                     # comando UP (faz upload de um arquivo - ao mesmo tempo que insere o conteúdo do mesmo)
            text = None
            print('Digite "end" (sem as aspas) numa linha em branco e pressione ENTER para enviar o texto.\n')
            print('Insira o texto abaixo:')
            while (text != 'end'):
                text = input()
                serverSock.send(str.encode(text))
        elif (command[0] == 'READ'):                            # comando CAT (visualiza o conteúdo do arquivo)
            fileName = ' '.join(command[1:])
            fileSize = int(messageStatus.split()[1])
            print('\nConteúdo do arquivo "{}":'.format(fileName))
            while (fileSize > 0):
                data = serverSock.recv(MESSAGE_SIZE)
                fileSize -= len(data)
                data = data.decode()
                print(data)

serverSock.close()                                              # encerra a conexão com o servidor