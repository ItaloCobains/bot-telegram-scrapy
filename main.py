from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.errors import SessionPasswordNeededError
import getpass
import sys
import csv
import traceback
import time
import random
import pyfiglet
#import re


class Bot:
    def __init__(self, api_id, api_hash, phone):
        self.api_id = api_id# Valor em inteiro   
        self.api_hash = api_hash   #str
        self.phone = phone      #str
        self.client = TelegramClient(self.phone, self.api_id, self.api_hash)
        self.client.connect()
        if not self.client.is_user_authorized():
            self.client.send_code_request(self.phone)
            self.client.sign_in(self.phone)
            try:
                self.client.sign_in(code=input('Enter code: '))
            except SessionPasswordNeededError:
                self.client.sign_in(password=getpass.getpass())

    def add_users_to_group(self):
        input_file = 'members.csv'
        users = []
        with open(input_file, encoding='UTF-8') as f:
            rows = csv.reader(f,delimiter=",",lineterminator="\n")
            next(rows, None)
            for row in rows:
                user = {}
                user['username'] = row[0]
                try:
                    user['id'] = int(row[1])
                    user['access_hash'] = int(row[2])
                except IndexError:
                    print ('\033[1;31musers without id or access_hash')
                users.append(user)

        random.shuffle(users)
        chats = []
        last_date = None
        chunk_size = 10
        groups=[]

        result = self.client(GetDialogsRequest(
                    offset_date=last_date,
                    offset_id=0,
                    offset_peer=InputPeerEmpty(),
                    limit=chunk_size,
                    hash = 0
                ))
        chats.extend(result.chats)

        for chat in chats:
            try:
                if chat.megagroup== True: #Condition To Only List Megagroups
                    groups.append(chat)
            except:
                continue

        print('\033[1;31mSelecione o grupo para adicionar os menbros:')
        i=0
        for group in groups:
            print(str(i) + '- ' + group.title)
            i+=1

        g_index = input("\033[1;31mEntre com um numero: ")
        target_group=groups[int(g_index)]
        print('\n\n\033[1;31mGrupo escolhido:\t' + groups[int(g_index)].title)

        target_group_entity = InputPeerChannel(target_group.id,target_group.access_hash)

        mode = int(input("\033[1;31mEntre com 1 para adicionar por username ou 2 pra adicionar por id: "))

        error_count = 0

        for user in users:
            try:
                print ("\033[1;31mAdd {}".format(user['username']))
                if mode == 1:
                    if user['username'] == "":
                        continue
                    user_to_add = self.client.get_input_entity(user['username'])
                elif mode == 2:
                    user_to_add = InputPeerUser(user['id'], user['access_hash'])
                else:
                    sys.exit("Invalid Mode Selected. Please Try Again.")
                self.client(InviteToChannelRequest(target_group_entity,[user_to_add]))
                print("\033[1;31mWaiting 60 Seconds...")
                time.sleep(60)
            except PeerFloodError:
                print("\033[1;31mObtendo o erro de inundação do telegrama. Você deve interromper o script agora. Tente novamente depois de algum tempo. ")
            except UserPrivacyRestrictedError:
                print("\033[1;31mAs configurações de privacidade do usuário não permitem que você faça isso. Pulando.")
            except:
                traceback.print_exc()
                print("\033[1;31mErro Inesperado")
                error_count += 1
                if error_count > 10:
                    sys.exit('\033[1;31mMuitos Erros')
                continue

    def list_users_in_group(self):
        chats = []
        last_date = None
        chunk_size = 200
        groups=[]
        
        result = self.client(GetDialogsRequest(
                    offset_date=last_date,
                    offset_id=0,
                    offset_peer=InputPeerEmpty(),
                    limit=chunk_size,
                    hash = 0
                ))
        chats.extend(result.chats)
        
        for chat in chats:
            try:
                print(chat)
                groups.append(chat)
                # if chat.megagroup== True:
            except:
                continue
        
        print('\033[1;31mEscolha o Grupo:')
        i=0
        for g in groups:
            print(str(i) + '- ' + g.title)
            i+=1
        
        g_index = input("\033[1;31mEntre com um numero: ")
        target_group=groups[int(g_index)]

        print('\n\n\033[1;31mGrupo elegido:\t' + groups[int(g_index)].title)
        
        print('\033[1;31mColetando Menbros...')
        all_participants = []
        all_participants = self.client.get_participants(target_group, aggressive=True)
        
        print('\033[1;31mSalvando no arquivo.csv...')
        with open("members.csv","w",encoding='UTF-8') as f:
            writer = csv.writer(f,delimiter=",",lineterminator="\n")
            writer.writerow(['username','user id', 'access hash','name','group', 'group id'])
            for user in all_participants:
                if user.username:
                    username= user.username
                else:
                    username= ""
                if user.first_name:
                    first_name= user.first_name
                else:
                    first_name= ""
                if user.last_name:
                    last_name= user.last_name
                else:
                    last_name= ""
                name= (first_name + ' ' + last_name).strip()
                writer.writerow([username,user.id,user.access_hash,name,target_group.title, target_group.id])      
        print('\033[1;31mMenbros Coletados com sucesso.')

    def printCSV(self):
        input_file = sys.argv[1]
        users = []
        with open(input_file, encoding='UTF-8') as f:
            rows = csv.reader(f,delimiter=",",lineterminator="\n")
            next(rows, None)
            for row in rows:
                user = {}
                user['username'] = row[0]
                user['id'] = int(row[1])
                user['access_hash'] = int(row[2])
                users.append(user)
                print(row)
                print(user)
        sys.exit('FINITO')


banner = pyfiglet.figlet_format('Italo Cobains')

print('\033[1;31m', banner)
print('Git Hub: https://github.com/ItaloCobains')
print('TWT: @MonoZezin')
print('Faça seu cadrastro na api do telegram. https://my.telegram.org')
print('caso ja tenha pode continuar')
print('Digite os paramentros pedidos: ')
api_id = int(input('Digite o seu api_id: '))
api_hash = input('Digite o seu api_hash: ')
phone = input('Digite o numero de telefone: ')

bot = Bot(api_id, api_hash, phone)

print('Digite um numero para uma ação: ')
modo = input('1-Scrapy contatos.\n2-Add contatos in group\n3-Show CSV\n')

if modo == '1':
    bot.list_users_in_group()
if modo == '2':
    bot.add_users_to_group()
if modo == '3':
    bot.printCSV()
else:
    print('Digite os paramentros corretos.')
    modo = input('1-Scrapy contatos.\n2-Add contatos in group\n3-Show CSV\n')
    if modo == '1':
        bot.list_users_in_group()
    if modo == '2':
        bot.add_users_to_group()
    if modo == '3':
        bot.printCSV()
