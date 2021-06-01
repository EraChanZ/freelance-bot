import vk_api
import requests
import json
import traceback
from vk_api import VkUpload
import random
from time import sleep
import datetime
from vk_api.longpoll import VkLongPoll, VkEventType
def is_number(smth):
    try:
        a = int(smth)
        return True
    except:
        return False
def my_round(chislo):
    if chislo//2 == chislo/2:
        return chislo//2
    else:
        return (chislo//2 + 1)
def get_all():
    return [i.replace('\n', '').split(':::') for i in open('database.txt','r').readlines()]
def get_zakazs():
    return [i.replace('\n','').split(':::') for i in open('orders.txt','r').readlines()]
def get_appl():
    return [i.replace('\n','').split(':::') for i in open('applications.txt','r').readlines()]
def find_matches(arr1,arr2):
    for a in arr2:
        if a in arr1:
            return True
    return False
session = requests.Session()
findinfo = {}
api_access_token = '****' # токен можно получить здесь https://qiwi.com/api
my_login = '*****' # номер QIWI Кошелька в формате +79991112233

s = requests.Session()
s.headers['authorization'] = 'Bearer ' + api_access_token
parameters = {'rows': '10'}
token = '******'
vk_session = vk_api.VkApi(token=token)
allskills = ["Работа с текстами","Дизайн","Программирование","Работа с переводами","Менеджмент","Интернет-реклама","Инженерия","аудио и видео","Веб-разработка"]
def make_unicode(input):
    return input
try:
    vk_session.auth(token_only=True)
except vk_api.AuthError as error_msg:
    print(error_msg)
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()
nsym = '#$%'
zakazinfo = {}
translate = {'Дальше':1,'Назад':-1}
for event in longpoll.listen():
    a = [i.replace('\n', '').split(':::') for i in list(open('orders.txt', 'r').readlines())]
    findic = {}
    for i in a:
        if i[1] not in list(findic.keys()):
            findic[i[1]] = {
                i[0]: {'owner_id': make_unicode(i[1]), 'skills': make_unicode(i[2]), 'price': make_unicode(i[3]),
                       'value': make_unicode(i[4]), 'text': make_unicode(i[5]),
                       'title': make_unicode(' '.join(i[5].split(' ')[:4]))}}
        else:
            findic[i[1]][i[0]] = {
                i[0]: {'owner_id': make_unicode(i[1]), 'skills': make_unicode(i[2]), 'price': make_unicode(i[3]),
                       'value': make_unicode(i[4]), 'text': make_unicode(i[5]),
                       'title': make_unicode(' '.join(i[5].split(' ')[:4]))}}
    try:
        with open('promocodes.json', 'r') as fp:
            promocodes = json.load(fp)
        allusers = get_all()
        users_data = {}
        paymenthistory = [i.replace('\n','') for i in open('payment.txt','r').readlines()]
        if allusers:
            users_data = {int(i[0]):{'balance':i[1],'status':i[2],'reputation':i[3],'info':i[4],'attachments':i[5]} for i in allusers}
        print(users_data)
        try:
            h = s.get('https://edge.qiwi.com/payment-history/v1/persons/' + my_login + '/payments', params=parameters)
            data = dict(json.loads(h.text))
            for d in data['data']:
                if d['comment']:
                    if is_number(d['comment'].replace(' ', '')):
                        if int(d['comment'].replace(' ', '')) in list(users_data.keys()):
                            if str(d['txnId']) not in paymenthistory:
                                print('Только что начислил')
                                users_data[int(d['comment'].replace(' ', ''))]['balance'] = str(int(users_data[int(d['comment'].replace(' ', ''))]['balance'])+int(str(d['sum']['amount'])))
                                vk.messages.send(
                                    user_id=int(d['comment'].replace(' ', '')),
                                    message='Вам на счет было начислено {} рублей'.format(str(d['sum']['amount'])),
                                    random_id=random.randint(1, 1000000000)
                                )
                                a = open('payment.txt','a')
                                a.write(str(d['txnId'])+'\n')
                                a.close()
        except:
            pass
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            if event.from_user:
                if event.user_id not in list(users_data.keys()):
                    vk.messages.send(
                        user_id = event.user_id,
                        message='Добро пожаловать новый пользователь !',
                        keyboard=open('keyboard.json',"r",encoding="UTF-8").read(),
                        random_id = random.randint(1,1000000000)
                    )
                    a = open('database.txt', 'a')
                    a.write(str(event.user_id) + ':' + '100' + ':' + 'user' + ':'+'0'+'\n')
                    users_data[event.user_id] = {'balance':'100','status':'user','reputation':'0','info':'Информация не добавлена','attachments':''}
                    a.close()
                else:
                    if event.user_id in list(findinfo.keys()):
                        if findinfo[event.user_id]['stage'] == 0:
                            if '/стоп' in event.text:
                                if findinfo[event.user_id]['skills']:
                                    findinfo[event.user_id]['stage'] += 1
                                    vk.messages.send(
                                        user_id=event.user_id,
                                        message='Выбранные навыки: {}\n '.format(','.join(findinfo[event.user_id]['skills'])),
                                        keyboard = open('backtomain.json', "r", encoding="UTF-8").read(),
                                        random_id=random.randint(1, 1000000000)
                                    )
                                    allzakazs = get_zakazs()
                                    match_zakazs = []
                                    for z in allzakazs:
                                        mch = find_matches(z[2].split(','), findinfo[event.user_id]['skills'])
                                        if mch:
                                            match_zakazs.append(z)
                                    if match_zakazs:
                                        vk.messages.send(
                                            user_id=event.user_id,
                                            message='Если заказ вам подходит, нажмите на соответствующую номеру заказа кнопку',
                                            random_id=random.randint(1, 1000000000)
                                        )
                                        for i in range(len(match_zakazs)):
                                            match_zakazs[i][4] = int(match_zakazs[i][4])
                                        match_zakazs = sorted(match_zakazs, key=lambda x: x[4],reverse=True)
                                        for i in range(len(match_zakazs)):
                                            match_zakazs[i][4] = str(match_zakazs[i][4])
                                        findinfo[event.user_id]['matched_orders'] = match_zakazs
                                        findinfo[event.user_id]['page'] += 1
                                        findinfo[event.user_id]['pages'] = my_round(len(match_zakazs))
                                        current_zakazs = findinfo[event.user_id]['matched_orders'][
                                                         (findinfo[event.user_id]['page'] - 1) * 2:(
                                                                     (findinfo[event.user_id]['page'] - 1) * 2 + 2)]
                                        c = 0
                                        msg = ''
                                        for cur in current_zakazs:
                                            c += 1
                                            msg += 'Заказ №{}\n{}\n Цена выполнения: {} рублей\nПриоритет: {}\n'.format(
                                                    c, cur[5].replace(nsym, '\n'), cur[3], cur[4])+'-----------\n'
                                            '''
                                            vk.messages.send(
                                                user_id=event.user_id,
                                                message='Заказ №{}\n{}\n Цена выполнения: {} рублей\nПриоритет: {}\n'.format(
                                                    c, cur[5].replace(nsym, '\n'), cur[3], cur[4]),
                                                keyboard=open('regulator.json', "r", encoding="UTF-8").read(),
                                                random_id=random.randint(1, 1000000000)
                                            )
                                            sleep(1)
                                            '''
                                        msg += 'Страница {}/{}'.format(findinfo[event.user_id]['page'],
                                                                            findinfo[event.user_id]['pages'])
                                        vk.messages.send(
                                            user_id=event.user_id,
                                            message=msg,
                                            keyboard=open('regulator.json', "r", encoding="UTF-8").read(),
                                            random_id=random.randint(1, 1000000000)
                                        )
                                        sleep(1)
                                    else:
                                        del findinfo[event.user_id]
                                        vk.messages.send(
                                            user_id=event.user_id,
                                            message='К сожалению заказов, соответствущих вашим навыков нету.\n Возвращаю вас в главное меню',
                                            keyboard=open('keyboard.json', "r", encoding="UTF-8").read(),
                                            random_id=random.randint(1, 1000000000)
                                        )
                                else:
                                    vk.messages.send(
                                        user_id=event.user_id,
                                        message='Вы не выбрали ни одного навыка.',
                                        keyboard=open('skills.json', "r", encoding="UTF-8").read(),
                                        random_id=random.randint(1, 1000000000)
                                    )
                            elif "/назад в меню" in event.text:
                                vk.messages.send(
                                    user_id=event.user_id,
                                    message='Вы вернулись в главное меню',
                                    keyboard=open('keyboard.json', "r", encoding="UTF-8").read(),
                                    random_id=random.randint(1, 1000000000)
                                )
                                del findinfo[event.user_id]
                            else:
                                if event.text in allskills and event.text not in findinfo[event.user_id]:
                                    vk.messages.send(
                                        user_id=event.user_id,
                                        message='Хорошо, добавил {} в список навыков'.format(event.text),
                                        random_id=random.randint(1, 1000000000)
                                    )
                                    findinfo[event.user_id]['skills'].append(event.text)
                        elif findinfo[event.user_id]['stage'] == 1:
                            if "/назад в меню" in event.text:
                                vk.messages.send(
                                    user_id=event.user_id,
                                    message='Вы вернулись в главное меню',
                                    keyboard=open('keyboard.json', "r", encoding="UTF-8").read(),
                                    random_id=random.randint(1, 1000000000)
                                )
                                del findinfo[event.user_id]
                            else:
                                if event.text in ['Дальше','Назад']:
                                    if int(findinfo[event.user_id]['page']) + translate[event.text] <= int(findinfo[event.user_id]['pages']) and int(findinfo[event.user_id]['page']) + translate[event.text] > 0:
                                        findinfo[event.user_id]['page'] += translate[event.text]
                                        current_zakazs = findinfo[event.user_id]['matched_orders'][
                                                         (findinfo[event.user_id]['page'] - 1) * 2:(
                                                                     (findinfo[event.user_id]['page'] - 1) * 2 + 2)]
                                        c = 0
                                        msg = ''
                                        for cur in current_zakazs:
                                            c += 1
                                            msg += 'Заказ №{}\n{}\n Цена выполнения: {} рублей\nПриоритет: {}\n'.format(c,cur[5].replace(nsym,'\n'),
                                                                                                                  cur[3],
                                                                                                                  cur[4])+'-----------\n'
                                            '''
                                            vk.messages.send(
                                                user_id=event.user_id,
                                                message='Заказ №{}\n{}\n Цена выполнения: {} рублей\nПриоритет: {}\n'.format(c,cur[5].replace(nsym,'\n'),
                                                                                                                  cur[3],
                                                                                                                  cur[4]),
                                                keyboard=open('regulator.json', "r", encoding="UTF-8").read(),
                                                random_id=random.randint(1, 1000000000)
                                            )
                                            sleep(1)
                                        '''
                                        msg += 'Страница {}/{}'.format(findinfo[event.user_id]['page'],
                                                                            findinfo[event.user_id]['pages'])

                                        vk.messages.send(
                                            user_id=event.user_id,
                                            message=msg,
                                            keyboard=open('regulator.json', "r", encoding="UTF-8").read(),
                                            random_id=random.randint(1, 1000000000)
                                        )
                                        sleep(1)
                                    elif int(findinfo[event.user_id]['page']) + translate[event.text] == 0:
                                        findinfo[event.user_id]['page'] = findinfo[event.user_id]['pages']
                                        current_zakazs = findinfo[event.user_id]['matched_orders'][
                                                         (findinfo[event.user_id]['page'] - 1) * 2:(
                                                                 (findinfo[event.user_id]['page'] - 1) * 2 + 2)]
                                        c = 0
                                        msg = ''
                                        for cur in current_zakazs:
                                            c += 1
                                            msg += 'Заказ №{}\n{}\n Цена выполнения: {} рублей\nПриоритет: {}\n'.format(c,
                                                                                                                        cur[
                                                                                                                            5].replace(
                                                                                                                            nsym,
                                                                                                                            '\n'),
                                                                                                                        cur[
                                                                                                                            3],
                                                                                                                        cur[
                                                                                                                            4]) + '-----------\n'
                                            '''
                                            vk.messages.send(
                                                user_id=event.user_id,
                                                message='Заказ №{}\n{}\n Цена выполнения: {} рублей\nПриоритет: {}\n'.format(c,cur[5].replace(nsym,'\n'),
                                                                                                                  cur[3],
                                                                                                                  cur[4]),
                                                keyboard=open('regulator.json', "r", encoding="UTF-8").read(),
                                                random_id=random.randint(1, 1000000000)
                                            )
                                            sleep(1)
                                        '''
                                        msg += 'Страница {}/{}'.format(findinfo[event.user_id]['page'],
                                                                       findinfo[event.user_id]['pages'])

                                        vk.messages.send(
                                            user_id=event.user_id,
                                            message=msg,
                                            keyboard=open('regulator.json', "r", encoding="UTF-8").read(),
                                            random_id=random.randint(1, 1000000000)
                                        )
                                        sleep(1)
                                    else:
                                        findinfo[event.user_id]['page'] = 1
                                        current_zakazs = findinfo[event.user_id]['matched_orders'][
                                                         (findinfo[event.user_id]['page'] - 1) * 2:(
                                                                 (findinfo[event.user_id]['page'] - 1) * 2 + 2)]
                                        c = 0
                                        msg = ''
                                        for cur in current_zakazs:
                                            c += 1
                                            msg += 'Заказ №{}\n{}\n Цена выполнения: {} рублей\nПриоритет: {}\n'.format(c,
                                                                                                                        cur[
                                                                                                                            5].replace(
                                                                                                                            nsym,
                                                                                                                            '\n'),
                                                                                                                        cur[
                                                                                                                            3],
                                                                                                                        cur[
                                                                                                                            4]) + '-----------\n'
                                            '''
                                            vk.messages.send(
                                                user_id=event.user_id,
                                                message='Заказ №{}\n{}\n Цена выполнения: {} рублей\nПриоритет: {}\n'.format(c,cur[5].replace(nsym,'\n'),
                                                                                                                  cur[3],
                                                                                                                  cur[4]),
                                                keyboard=open('regulator.json', "r", encoding="UTF-8").read(),
                                                random_id=random.randint(1, 1000000000)
                                            )
                                            sleep(1)
                                        '''
                                        msg += 'Страница {}/{}'.format(findinfo[event.user_id]['page'],
                                                                       findinfo[event.user_id]['pages'])

                                        vk.messages.send(
                                            user_id=event.user_id,
                                            message=msg,
                                            keyboard=open('regulator.json', "r", encoding="UTF-8").read(),
                                            random_id=random.randint(1, 1000000000)
                                        )
                                        sleep(1)
                                elif event.text.replace('заказ ','') in ['1','2']:
                                    if (int(findinfo[event.user_id]['page'])-1)*2+(int(event.text.replace('заказ ',''))-1) < ((int(findinfo[event.user_id]['pages'])*2)):
                                        vk.messages.send(
                                            user_id=event.user_id,
                                            message='Теперь вы должны кратко описать реализацию этой задачи и почему именно вам должны ее доверить.',
                                            keyboard=open('backtomain.json', "r", encoding="UTF-8").read(),
                                            random_id=random.randint(1, 1000000000)
                                        )
                                        findinfo[event.user_id]['chosen'] = (int(findinfo[event.user_id]['page'])-1)*2+(int(event.text.replace('заказ ',''))-1)
                                        findinfo[event.user_id]['stage'] += 1
                        elif findinfo[event.user_id]['stage'] == 2:
                            if "/назад в меню" in event.text:
                                vk.messages.send(
                                    user_id=event.user_id,
                                    message='Вы вернулись в главное меню',
                                    keyboard=open('keyboard.json', "r", encoding="UTF-8").read(),
                                    random_id=random.randint(1, 1000000000)
                                )
                                del findinfo[event.user_id]
                            else:
                                aplfile = open('applications.txt','a')
                                aplfile.write(str(event.user_id)+':::'+findinfo[event.user_id]['matched_orders'][findinfo[event.user_id]['chosen']][1]+":::"+findinfo[event.user_id]['matched_orders'][findinfo[event.user_id]['chosen']][5]+':::'+event.text+':::'+findinfo[event.user_id]['matched_orders'][findinfo[event.user_id]['chosen']][0]+'\n')
                                aplfile.close()
                                vk.messages.send(
                                    user_id=event.user_id,
                                    message='Ваша заявка успешно сохранена и отправлена заказчику\nСписано 30 монет',
                                    keyboard=open('keyboard.json', "r", encoding="UTF-8").read(),
                                    random_id=random.randint(1, 1000000000)
                                )
                                users_data[event.user_id]['balance'] = str(int(users_data[event.user_id]['balance'])- 30)
                                del findinfo[event.user_id]
                    elif event.user_id in list(zakazinfo.keys()):
                        if zakazinfo[event.user_id]['stage'] == 0:
                            if '/стоп' in event.text:
                                if zakazinfo[event.user_id]['skills']:
                                    zakazinfo[event.user_id]['stage'] += 1
                                    vk.messages.send(
                                        user_id=event.user_id,
                                        message='Выбранные навыки: {}\n Теперь вам нужно вписать краткое Техническое задание и требования к исполнителю'.format(','.join(zakazinfo[event.user_id]['skills'])),
                                        keyboard = open('backtomain.json', "r", encoding="UTF-8").read(),
                                        random_id=random.randint(1, 1000000000)
                                    )
                                else:
                                    vk.messages.send(
                                        user_id=event.user_id,
                                        message='Вы не выбрали ни одного навыка.',
                                        keyboard=open('skills.json', "r", encoding="UTF-8").read(),
                                        random_id=random.randint(1, 1000000000)
                                    )
                            elif "/назад в меню" in event.text:
                                vk.messages.send(
                                    user_id=event.user_id,
                                    message='Вы вернулись в главное меню',
                                    keyboard=open('keyboard.json', "r", encoding="UTF-8").read(),
                                    random_id=random.randint(1, 1000000000)
                                )
                                del zakazinfo[event.user_id]
                            else:
                                if event.text in allskills and event.text not in zakazinfo[event.user_id]['skills']:
                                    zakazinfo[event.user_id]['skills'].append(event.text)
                                    vk.messages.send(
                                        user_id=event.user_id,
                                        message='Хорошо, добавил {} в список навыков'.format(event.text),
                                        random_id=random.randint(1, 1000000000)
                                    )
                        elif zakazinfo[event.user_id]['stage'] == 1:
                            if "/назад в меню" in event.text:
                                del zakazinfo[event.user_id]
                                vk.messages.send(
                                    user_id=event.user_id,
                                    message='Вы вернулись в главное меню',
                                    keyboard=open('keyboard.json', "r", encoding="UTF-8").read(),
                                    random_id=random.randint(1, 1000000000)
                                )
                            else:
                                zakazinfo[event.user_id]['text'] = event.text
                                vk.messages.send(
                                    user_id=event.user_id,
                                    message='За какую цену вы хотите разместить ваш заказ? Чем больше цена, тем выше в списке заданий будет ваше объявление\n (Либо выберете из готовых кнопок, либо впишите число сами)',
                                    keyboard=open('costs.json', "r", encoding="UTF-8").read(),
                                    random_id=random.randint(1, 1000000000)
                                )
                                zakazinfo[event.user_id]['stage'] += 1
                        elif zakazinfo[event.user_id]['stage'] == 2:
                            if "/назад в меню" in event.text:
                                del zakazinfo[event.user_id]
                                vk.messages.send(
                                    user_id=event.user_id,
                                    message='Вы вернулись в главное меню',
                                    keyboard=open('keyboard.json', "r", encoding="UTF-8").read(),
                                    random_id=random.randint(1, 1000000000)
                                )
                            else:
                                if is_number(event.text):
                                    if int(event.text) <= int(users_data[event.user_id]['balance']) and int(event.text)>=50:
                                        zakazinfo[event.user_id]['value'] = int(event.text)
                                        zakazinfo[event.user_id]['stage'] += 1
                                        vk.messages.send(
                                            user_id=event.user_id,
                                            message='Теперь впишите цену выполнения заказа в рублях',
                                            keyboard=open('backtomain.json', "r", encoding="UTF-8").read(),
                                            random_id=random.randint(1, 1000000000)
                                        )
                                    else:
                                        vk.messages.send(
                                            user_id=event.user_id,
                                            message='Недостаточно средств, или цена меньше 50',
                                            keyboard=open('costs.json', "r", encoding="UTF-8").read(),
                                            random_id=random.randint(1, 1000000000)
                                        )
                                else:
                                    vk.messages.send(
                                        user_id=event.user_id,
                                        message='Это не цифра!',
                                        keyboard=open('costs.json', "r", encoding="UTF-8").read(),
                                        random_id=random.randint(1, 1000000000))
                        elif zakazinfo[event.user_id]['stage'] == 3:
                            if '/назад в меню' in event.text:
                                del zakazinfo[event.user_id]
                                vk.messages.send(
                                    user_id=event.user_id,
                                    message='Вы вернулись в главное меню',
                                    keyboard=open('keyboard.json', "r", encoding="UTF-8").read(),
                                    random_id=random.randint(1, 1000000000)
                                )
                            else:
                                if is_number(event.text):
                                    zakazinfo[event.user_id]['price'] = int(event.text)
                                    vk.messages.send(
                                        user_id=event.user_id,
                                        message='Конфигурация вашего заказа:\nЦена размещения: {}\nЦена выполнения: {} рублей\nНавыки исполнителя: {}\nТекст :{}\nПодтверждаете заказ?'.format(str(zakazinfo[event.user_id]['value']),str(zakazinfo[event.user_id]['price']),','.join(zakazinfo[event.user_id]['skills']),zakazinfo[event.user_id]['text']),
                                        keyboard=open('confirm.json', "r", encoding="UTF-8").read(),
                                        random_id=random.randint(1, 1000000000)
                                    )
                                    zakazinfo[event.user_id]['stage'] += 1
                                else:
                                    vk.messages.send(
                                        user_id=event.user_id,
                                        message='Вы должны ввести число, цена выполнения заказа в рублях',
                                        random_id=random.randint(1, 1000000000)
                                    )
                        elif zakazinfo[event.user_id]['stage'] == 4:
                            if '/назад в меню' in event.text:
                                del zakazinfo[event.user_id]
                                vk.messages.send(
                                    user_id=event.user_id,
                                    message='Вы вернулись в главное меню',
                                    keyboard=open('keyboard.json', "r", encoding="UTF-8").read(),
                                    random_id=random.randint(1, 1000000000)
                                )
                            elif event.text == 'Да':
                                file = open('orders.txt','a')
                                file.write(str(len(open('orders.txt','r').readlines())+1)+':::'+str(event.user_id)+':::'+','.join(zakazinfo[event.user_id]['skills'])+':::'+str(zakazinfo[event.user_id]['price'])+':::'+str(zakazinfo[event.user_id]['value'])+':::'+zakazinfo[event.user_id]['text'].replace('\n','#$%')+'\n')
                                file.close()
                                vk.messages.send(
                                    user_id=event.user_id,
                                    message='Ваш заказ успешно занесен в базу данных! \nСписано {} монет\nТеперь вы в главном меню.'.format(zakazinfo[event.user_id]['value']),
                                    keyboard=open('keyboard.json', "r", encoding="UTF-8").read(),
                                    random_id=random.randint(1, 1000000000)
                                )
                                users_data[event.user_id]['balance'] = str(int(users_data[event.user_id]['balance']) - zakazinfo[event.user_id]['value'])
                                del zakazinfo[event.user_id]
                            elif event.text == 'Нет':
                                del zakazinfo[event.user_id]
                                vk.messages.send(
                                    user_id=event.user_id,
                                    message='Вы вернулись в главное меню',
                                    keyboard = open('keyboard.json', "r", encoding="UTF-8").read(),
                                    random_id=random.randint(1, 1000000000)
                                )
                    elif '/лк' in event.text.lower():
                        vk.messages.send(
                            user_id=event.user_id,
                            message='Личная информация: {}\nВаш баланс: {} монет\nВаш статус: {}\nОчки репутации: {}\n'.format(users_data[event.user_id]['info'].replace(nsym,'\n'),users_data[event.user_id]['balance'],users_data[event.user_id]['status'],users_data[event.user_id]['reputation']),
                            random_id=random.randint(1, 1000000000)
                        )
                    elif '/инфо' in event.text.lower() or 'помощь' in event.text.lower() or 'команды' in event.text.lower():
                        vk.messages.send(
                            user_id=event.user_id,
                            message='/лк - личная информация\n/инфо - информационное сообщение\n/заказ - сделать заказ\n/найти - найти заказ\n/прайс - Цены на различные действия\n/о себе {текст о себе} (вы добавляете общедоступную информацию про себя)\n/узнать {ID юзера} (кидает вам личную информацию о данном пользователе)\n/очистить (Очищает все заявки на ваши задания)\n /промокод {сам промокод}\n/какпополнить Кидает вам информацию о пополнение счёта',
                            random_id=random.randint(1, 1000000000)
                        )
                    elif '/пополнить ' in event.text.lower() and users_data[event.user_id]['status'] == 'moder':
                        if is_number(event.text.lower().replace('/пополнить ','').split(' ')[0]) and is_number(event.text.lower().replace('/пополнить ','').split(' ')[1]):
                            if int(event.text.lower().replace('/пополнить ','').split(' ')[0]) in list(users_data.keys()):
                                users_data[int(event.text.lower().replace('/пополнить ','').split(' ')[0])]['balance'] = str(int(users_data[int(event.text.lower().replace('/пополнить ','').split(' ')[0])]['balance'])+int(event.text.lower().replace('/пополнить ','').split(' ')[1]))
                                vk.messages.send(
                                    user_id=event.user_id,
                                    message='Успешно!',
                                    random_id=random.randint(1, 1000000000)
                                )
                    elif '/реп ' in event.text.lower() and users_data[event.user_id]['status'] == 'moder':
                        if is_number(event.text.lower().replace('/реп ','').split(' ')[0]) and is_number(event.text.lower().replace('/реп ','').split(' ')[1]):
                            if int(event.text.lower().replace('/реп ','').split(' ')[0]) in list(users_data.keys()):
                                users_data[int(event.text.lower().replace('/реп ','').split(' ')[0])]['reputation'] = str(int(users_data[int(event.text.lower().replace('/реп ','').split(' ')[0])]['reputation'])+int(event.text.lower().replace('/реп ','').split(' ')[1]))
                                vk.messages.send(
                                    user_id=event.user_id,
                                    message='Успешно!',
                                    random_id=random.randint(1, 1000000000)
                                )
                    elif '/узнать ' in event.text.lower():
                        if is_number(event.text.replace('/узнать ','')):
                            if int(event.text.replace('/узнать ','')) in list(users_data.keys()):
                                vk.messages.send(
                                    user_id=event.user_id,
                                    message=users_data[int(event.text.replace('/узнать ',''))]['info'],
                                    attachment = users_data[int(event.text.replace('/узнать ',''))]['attachments'][:-1],
                                    random_id=random.randint(1, 1000000000)
                                )
                            else:
                                vk.messages.send(
                                    user_id=event.user_id,
                                    message='Пользователя с таким ID не найдено',
                                    random_id=random.randint(1, 1000000000)
                                )
                        else:
                            vk.messages.send(
                                user_id=event.user_id,
                                message='Пользователя с таким ID не найдено',
                                random_id=random.randint(1, 1000000000)
                            )
                    elif '/прайс' in event.text.lower():
                        vk.messages.send(
                            user_id=event.user_id,
                            message='Минимальная ставка заказа - 50 монет, чем больше будет цена размещения заказа, тем выше в списке он будет находится \n Чтобы подать заявку на заказ - 30 монет',
                            random_id=random.randint(1, 1000000000)
                        )
                    elif '/заказ' in event.text.lower():
                        if int(users_data[event.user_id]['reputation']) < -100:
                            vk.messages.send(
                                user_id=event.user_id,
                                message='К сожалению ваша репутация ниже -100 баллов. Вы не сможете сделать заказ',
                                random_id=random.randint(1, 1000000000)
                            )
                        else:
                            zakazinfo[event.user_id] = {'stage':0,'skills':[],'value':50,'text':'','attachments':[],'price':0}
                            vk.messages.send(
                                user_id=event.user_id,
                                message='Пожалуйста, выберите какими навыками должен обладать исполнитель?\n Если вы уже выбрали все навыки, нажмите стоп.',
                                keyboard=open('skills.json',"r",encoding="UTF-8").read(),
                                random_id=random.randint(1, 1000000000)
                            )
                    elif '/о себе ' in event.text.lower():
                        users_data[event.user_id]['info'] = event.text.replace('/о себе ','').replace('\n',nsym)
                        if event.attachments:
                            users_data[event.user_id]['attachments'] = ''
                            for i in event.attachments:
                                if 'type' not in i:
                                    users_data[event.user_id]['attachments'] += 'photo'+event.attachments[i]+','
                        vk.messages.send(
                            user_id=event.user_id,
                            message='Вы добавили информацию о себе,её сможет увидеть любой пользователь',
                            random_id=random.randint(1, 1000000000)
                        )
                    elif '/очистить' in event.text.lower():
                        aff = get_appl()
                        final = []
                        for a in aff:
                            if a[1] != str(event.user_id):
                                final.append(a)
                        dang = open('applications.txt','w')
                        for f in final:
                            dang.write(':::'.join(f)+'\n')
                        dang.close()
                        vk.messages.send(
                            user_id=event.user_id,
                            message='Все заявки были очищены',
                            random_id=random.randint(1, 1000000000)
                        )
                    elif '/заявки' in event.text.lower():
                        all_appl = get_appl()
                        sovp = [i for i in all_appl if i[1] == str(event.user_id)]
                        if sovp:
                            f_sovp = []
                            for s in sovp:
                                f_sovp.append('Заявка на заказ: {}\n[id{}|Исполнитель]\n{}\n--------------'.format(' '.join(s[2].split(' ')[:4]),s[0],s[3]))
                            sendings = []
                            for i in range(0,len(sovp),4):
                                sendings.append('\n'.join(f_sovp[i:i+4]))
                            for s in sendings:
                                vk.messages.send(
                                    user_id=event.user_id,
                                    message=s,
                                    random_id=random.randint(1, 1000000000)
                                )
                        else:
                            vk.messages.send(
                                user_id=event.user_id,
                                message='Заявок пока что нету.',
                                random_id=random.randint(1, 1000000000)
                            )
                    elif '/сздпрм ' in event.text.lower() and users_data[event.user_id]['status'] == 'moder':
                        pr_data = event.text.lower().replace('/сздпрм ','').split(' ')
                        promocodes[pr_data[0]] = {'value':pr_data[1],'trans':'0','users':''}
                        vk.messages.send(
                            user_id=event.user_id,
                            message='Промокод создан',
                            random_id=random.randint(1, 1000000000)
                        )
                    elif '/какпополнить' in event.text.lower():
                        vk.messages.send(
                            user_id=event.user_id,
                            message='Чтобы пополнить ваш баланс монеток - вам нужно закинуть сумму в рублях на аккаунт QIWI кошелька (+79261572269) и в комментариях к платежу указать свой ВК ID, ваш ID:{}.\nПомните, что платежи проверяет бот, соответственно кроме вашего ID в комментариях ничего не пишите. Если платеж не пришёл в течении 12 часов - напишите [id281303430|ЕМУ]\nНужно будет заскринить информацию об оплате'.format(str(event.user_id)),
                            random_id=random.randint(1, 1000000000)
                        )
                    elif '/промокод ' in event.text.lower():
                        promo = event.text.lower().replace('/промокод ','')
                        if promo in list(promocodes.keys()):
                            if str(event.user_id) in promocodes[promo]['users']:
                                vk.messages.send(
                                    user_id=event.user_id,
                                    message='Вы уже вводили данный промокод',
                                    random_id=random.randint(1, 1000000000)
                                )
                            else:
                                promocodes[promo]['users'] += str(event.user_id) + ','
                                promocodes[promo]['trans'] = str(int(promocodes[promo]['trans']) + 1)
                                users_data[event.user_id]['balance'] = str(int(users_data[event.user_id]['balance']) + int(promocodes[promo]['value']))
                                vk.messages.send(
                                    user_id=event.user_id,
                                    message='На ваш счёт было начислено {} монеток'.format(promocodes[promo]['value']),
                                    random_id=random.randint(1, 1000000000)
                                )
                        else:
                            vk.messages.send(
                                user_id=event.user_id,
                                message='Промокод не найден или срок действия истёк',
                                random_id=random.randint(1, 1000000000)
                            )
                    elif '/найти' in event.text.lower():
                        if int(users_data[event.user_id]['reputation']) < -100:
                            vk.messages.send(
                                user_id=event.user_id,
                                message='К сожалению ваша репутация ниже -100 баллов. Вы не сможете взять заказ',
                                random_id=random.randint(1, 1000000000)
                            )
                        elif int(users_data[event.user_id]['balance']) < 30:
                            vk.messages.send(
                                user_id=event.user_id,
                                message='К сожалению ваш баланс ниже 30 монет. Вы не сможете взять заказ',
                                random_id=random.randint(1, 1000000000)
                            )
                        else:
                            findinfo[event.user_id] = {'stage':0,'skills':[],'text':'','attachments':[],'page':0,'matched_orders':[],'pages':0,'chosen':0}
                            vk.messages.send(
                                user_id=event.user_id,
                                message='Пожалуйста, выберете навыки, которыми вы обладаете.\n Нажмите на стоп, когда выберите все',
                                keyboard=open('skills.json', "r", encoding="UTF-8").read(),
                                random_id=random.randint(1, 1000000000)
                            )
                    else:
                        vk.messages.send(
                            user_id=event.user_id,
                            message='Команда неизвестна.',
                            keyboard=open('keyboard.json', "r", encoding="UTF-8").read(),
                            random_id=random.randint(1, 1000000000)
                        )
        f = open('database.txt', 'w')
        for i in users_data:
            f.write(str(i)+':::'+users_data[int(i)]['balance']+':::'+users_data[int(i)]['status']+':::'+users_data[int(i)]['reputation']+':::'+users_data[int(i)]['info']+':::'+users_data[int(i)]['attachments']+'\n')
        f.close()
        with open('promocodes.json', 'w') as fp:
            json.dump(promocodes, fp)
    except Exception as e:
        print(e)
