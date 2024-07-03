# vscode에서 현재경로 문제로 인해 추가
import os
parent2_path = os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))
parent1_path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
folder_path = os.path.dirname(os.path.abspath(__file__))

#import email_parsing
import sys
sys.path.append(parent1_path)   # 상위폴더 import
#import category_template
import ledger

import openpyxl
import datetime
import csv
import re

# vscode에서 현재경로 문제로 인해 추가
os.chdir(folder_path)

if __name__ == '__main__':
    messages = []

    csv_files = ['신한.csv', '우리.csv', '현대.csv'] # iBackup_Viewer
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
        infos = ledger.processMessages2CsvData(messages)
        ledger.makeCSV(infos)
        
    except Exception as e:
        print('Exception', e)