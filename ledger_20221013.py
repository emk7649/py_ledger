import email_parsing
import category_template

if __name__ == '__main__':
    try:
        count_item = 0
        email = email_parsing.Email()
        messages = email.messages
        #messages = messages[-1:]
        for msg in messages:
            #print(msg)
            #print('')
            items = msg.split('[Web발신]')
            items = items[1:]
            #print(len(items))

            if len(items) == 0 :    # [Web발신] 아닌 경우 중 단건
                lines = msg.split('\n')
                lines = lines[2:]
                items.append('\n'.join(lines))

            for item in items:
                count_item += 1
                item = item.strip()
                item = item.replace('\r\n', '\n')
                
                info = category_template.transform(item)
                
                if info == '':
                    print(item)
                #if len(info) > 3 and info[3] == '[현대카드] 자동납부':
                #    print(item)
                #    print(info)
                if info != '':
                    print(info)
        
        print(''.join(['count_item: ', str(count_item)]))        
        category_template.print_template()
        
    except Exception as e:
        print('Exception', e)
