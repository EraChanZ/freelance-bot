import vk_api
import requests
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
    print(arr1,arr2)
    for a in arr2:
        if a in arr1:
            return True
    return False
session = requests.Session()
findinfo = {}
token = '34925231a2be99ea9f7af0e19ecde0308fe33b2fe961d605b40a5023734c7a27cb8305f78b1da9051d3bc'
login, password = '+79261572269', 'convneural123'
vk_session = vk_api.VkApi(token=token)
vk_sessionu = vk_api.VkApi(login, password)
upload = VkUpload(vk_sessionu)
allskills = ["Работа с текстами","Дизайн","Программирование","Работа с переводами","Менеджмент","Интернет-реклама","Инженерия","аудио и видео","Веб-разработка"]
try:
    vk_sessionu.auth(token_only=True)
except vk_api.AuthError as error_msg:
    print(error_msg)
try:
    vk_session.auth(token_only=True)
except vk_api.AuthError as error_msg:
    print(error_msg)
longpoll = VkLongPoll(vk_session)
vku = vk_sessionu.get_api()
vk = vk_session.get_api()
nsym = '#$%'
zakazinfo = {}
translate = {'Дальше':1,'Назад':-1}
for event in longpoll.listen():
    allusers = get_all()
    users_data = {}
    if allusers:
        users_data = {int(i[0]):{'balance':i[1],'status':i[2],'reputation':i[3],'info':i[4]} for i in allusers}
    print(users_data)
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
        print('kek')
        if event.from_user:
            if event.user_id not in list(users_data.keys()):
                vk.messages.send(
                    user_id = event.user_id,
                    message='Добро пожаловать новый пользователь !',keyboard=open('keyboard.json',"r",encoding="UTF-8").read(),
                    random_id = random.randint(1,1000000000)
                )
                a = open('database.txt', 'a')
                a.write(str(event.user_id) + ':' + '100' + ':' + 'user' + ':'+'0'+'\n')
                users_data[event.user_id] = {'balance':'100','status':'user','reputation':'0','info':''}
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
                                print(allzakazs)
                                match_zakazs = []
                                print(findinfo[event.user_id]['skills'])
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
                                    match_zakazs = sorted(match_zakazs, key=lambda x: x[4], reverse=True)
                                    findinfo[event.user_id]['matched_orders'] = match_zakazs
                                    findinfo[event.user_id]['page'] += 1
                                    findinfo[event.user_id]['pages'] = my_round(len(match_zakazs))
                                    current_zakazs = findinfo[event.user_id]['matched_orders'][
                                                     (findinfo[event.user_id]['page'] - 1) * 2:(
                                                                 (findinfo[event.user_id]['page'] - 1) * 2 + 2)]
                                    c = 0
                                    for cur in current_zakazs:
                                        c += 1
                                        vk.messages.send(
                                            user_id=event.user_id,
                                            message='Заказ №{}\n{}\n Цена выполнения: {} рублей\nПриоритет: {}\n'.format(
                                                c, cur[5].replace(nsym, '\n'), cur[3], cur[4]),
                                            keyboard=open('regulator.json', "r", encoding="UTF-8").read(),
                                            random_id=random.randint(1, 1000000000)
                                        )
                                        sleep(1)
                                    vk.messages.send(
                                        user_id=event.user_id,
                                        message='Страница {}/{}'.format(findinfo[event.user_id]['page'],
                                                                        findinfo[event.user_id]['pages']),
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
                                if int(findinfo[event.user_id]['page']) + translate[event.text] < int(findinfo[event.user_id]['pages']) and int(findinfo[event.user_id]['page']) + translate[event.text] > 0:
                                    findinfo[event.user_id]['page'] += translate[event.text]
                                    current_zakazs = findinfo[event.user_id]['matched_orders'][
                                                     (findinfo[event.user_id]['page'] - 1) * 2:(
                                                                 (findinfo[event.user_id]['page'] - 1) * 2 + 2)]
                                    c = 0
                                    for cur in current_zakazs:
                                        c += 1
                                        vk.messages.send(
                                            user_id=event.user_id,
                                            message='Заказ №{}\n{}\n Цена выполнения: {} рублей\nПриоритет: {}\n'.format(c,cur[5].replace(nsym,'\n'),
                                                                                                              cur[3],
                                                                                                              cur[4]),
                                            keyboard=open('regulator.json', "r", encoding="UTF-8").read(),
                                            random_id=random.randint(1, 1000000000)
                                        )
                                        sleep(1)
                                    vk.messages.send(
                                        user_id=event.user_id,
                                        message='Страница {}/{}'.format(findinfo[event.user_id]['page'],
                                                                        findinfo[event.user_id]['pages']),
                                        random_id=random.randint(1, 1000000000)
                                    )
                                    sleep(1)
                            elif event.text in ['1','2']:
                                vk.messages.send(
                                    user_id=event.user_id,
                                    message='Теперь вы должны кратко описать реализацию этой задачи и почему именно вам должны ее доверить.',
                                    keyboard=open('backtomain.json', "r", encoding="UTF-8").read(),
                                    random_id=random.randint(1, 1000000000)
                                )
                                findinfo[event.user_id]['chosen'] = (int(findinfo[event.user_id]['page'])-1)*2+(int(event.text)-1)
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
                            aplfile.write(str(event.user_id)+':::'+findinfo[event.user_id]['matched_orders'][findinfo[event.user_id]['chosen']][1]+':::'+findinfo[event.user_id]['matched_orders'][findinfo[event.user_id]['chosen']][5]+':::'+event.text+'\n')
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
                                message='За какую цену вы хотите разместить ваш заказ?\n (Либо выберете из готовых кнопок, либо впишите число сами)',
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
                                    message='Конфигурация вашего заказа:\nЦена размещения: {}\nЦена выполнения: {} рублей\nНавыки исполнителя: {}\nТекст :{}'.format(str(zakazinfo[event.user_id]['value']),str(zakazinfo[event.user_id]['price']),','.join(zakazinfo[event.user_id]['skills']),zakazinfo[event.user_id]['text']),
                                    random_id=random.randint(1, 1000000000)
                                )
                                sleep(1)
                                vk.messages.send(
                                    user_id=event.user_id,
                                    message='Подтверждаете заказ?',
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
                        message='Личная информация: {}\nВаш баланс: {} монет\nВаш статус: {}\nОчки репутации: {}\nЧтобы пополнить ваш баланс монеток - пишите [id281303430|ЕМУ]'.format(users_data[event.user_id]['info'].replace(nsym,'\n'),users_data[event.user_id]['balance'],users_data[event.user_id]['status'],users_data[event.user_id]['reputation']),
                        random_id=random.randint(1, 1000000000)
                    )
                elif '/инфо' in event.text.lower():
                    vk.messages.send(
                        user_id=event.user_id,
                        message='/лк - личная информация\n/инфо - информационное сообщение\n/заказ - сделать заказ\n/найти - найти заказ\n/прайс - Цены на различные действия\n/о себе {текст о себе} (вы добавляете общедоступную информацию про себя)\n/узнать {ID юзера} (кидает вам личную информацию о данном пользователе)\n/очистить (Очищает все заявки на ваши задания)',
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
                            f_sovp.append('[id{}|Исполнитель]\n{}\n--------------'.format(s[0],s[3]))
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
        print()
        f.write(str(i)+':::'+users_data[int(i)]['balance']+':::'+users_data[int(i)]['status']+':::'+users_data[int(i)]['reputation']+':::'+users_data[int(i)]['info']+'\n')
    f.close()