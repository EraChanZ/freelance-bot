import json
def make_unicode(input):
    return input
a = [i.replace('\n','').split(':::') for i in list(open('orders.txt','r').readlines())]
findic = {}
for i in a:
    if i[1] not in list(findic.keys()):
        findic[i[1]] = {i[0]:{'owner_id':make_unicode(i[1]),'skills':make_unicode(i[2]),'price':make_unicode(i[3]),'value':make_unicode(i[4]),'text':make_unicode(i[5]),'title':make_unicode(' '.join(i[5].split(' ')[:4]))}}
    else:
        findic[i[1]][i[0]] = {i[0]:{'owner_id':make_unicode(i[1]),'skills':make_unicode(i[2]),'price':make_unicode(i[3]),'value':make_unicode(i[4]),'text':make_unicode(i[5]),'title':make_unicode(' '.join(i[5].split(' ')[:4]))}}
