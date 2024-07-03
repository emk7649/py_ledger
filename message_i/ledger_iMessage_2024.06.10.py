# vscode에서 현재경로 문제로 인해 추가
import os
parent2_path = os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))
parent1_path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
folder_path = os.path.dirname(os.path.abspath(__file__))

#import email_parsing
import sys
sys.path.append(parent1_path)   # 상위폴더 import
import category_template
import ledger

import openpyxl
import datetime
import csv
import re

# vscode에서 현재경로 문제로 인해 추가
os.chdir(folder_path)

if __name__ == '__main__':
    messages = []

    csv_files = ['신한.csv', '우리.csv', '현대.csv']
    for file in csv_files:
        if not os.path.exists(file):
            continue
        f = open(file,'r', encoding='UTF8')
        rdr = csv.reader(f)
        for i, line in enumerate(rdr):
            if(len(line) < 5):
                continue

            data = line[0]
            regex = r'''\d\d\d\d'''
            searchObj = re.search(regex, data)
            if searchObj is not None:
                # inline 중에도 사용할 수 있도록 [Web발신] 옆에 str_year 붙이기
                year = searchObj.group()
                line[4] = line[4].replace('[Web발신]', f'[Web발신]{year}')
                messages.append(line[4])
        f.close()

    try:
        categoryTemplate = category_template.category_template()
        infos = []
        count_item = 0
        #messages = messages[-1:]
        for msg in messages:
            #print(msg)
            #print('')

            # 하나의 메시지는 하나의 Item
            # [Web발신] 있으면 \n까지 지우기
            # [Web발신]\d\d\d\d 있으면 (\d\d\d\d) -> year 치환
            lines = msg.split('\n')
            if len(lines) == 0 :
                continue
            if '[Web발신]' in lines[0] :
                regex = r'''\[Web발신\](\d\d\d\d)'''
                searchObj = re.search(regex, lines[0])
                if searchObj is not None:
                    year = searchObj.groups()[0]
                    lines = lines[1:]
                else:
                    lines = lines[0:]
                item = '\n'.join(lines)

                count_item += 1
                item = item.strip()
                item = item.replace('\r\n', '\n')
                
                record = categoryTemplate.processData2Record(item, int(year))
                
                #re-matching fail:msg str, re-matching success:list_sorted
                if record == '':
                    print(item)
                    infos.append(item)
                if record != '':
                    print(record)
                    infos.append(record)
        
        print(''.join(['count_item: ', str(count_item)]))        
        categoryTemplate.print_template()
        
        ledger.makeCSV(infos)
        
    except Exception as e:
        print('Exception', e)