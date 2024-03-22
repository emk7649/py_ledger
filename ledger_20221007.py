import email_parsing
import re
import sys

def transform(data):
    date = ''
    amount = 0
    payment = '우리체크1'
    agent = ''
    category = '주거가구'
    memo = '책상'
    return (date, amount, payment, agent, category, memo)

if __name__ == '__main__':
    try:
        email = email_parsing.Email()
        messages = email.messages
        messages = messages[-1:]
        for msg in messages:
            #print(msg)
            #print('')
            items = msg.split('[Web발신]')
            items = items[1:]
            print(len(items))
            for item in items:
                item = item.strip()
                item = item.replace('\r\n', '\n')
                
                print(re.match(rrrr, item))
                print(rrrr)
                print(item)
                
                #print(item)
                #print('')
                #print(rrrr)
            
            
        
    except Exception as e:
        print('Exception', e)
