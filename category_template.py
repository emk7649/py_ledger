#from functools import total_ordering
import re, os
import datetime
from dateutil.parser import parse # for 날짜시간 format
from dateutil.relativedelta import relativedelta

import FinanceDataReader as fdr
usd = fdr.DataReader('USD/KRW', '2018-01-01')['Close']
jpy = fdr.DataReader('JPY/KRW', '2018-01-01')['Close']
cny = 190 #위 코드로 cny를 불러올 때 문제가 있어 일단 하드코딩
gbp = 1700
aud = 900
exchange_rate = 1.04

# vscode에서 현재경로 문제로 인해 추가
folder_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(folder_path)

# 2023.11.21 각 메시지_template class마다 example 변수로 관리 → class, .txt로 관리
# 2024.6.7, 2024.3.27 작업한 getDate, getExchange 정리
class example_manager():
	examples = {}

	def __init__(self):
		f = open("category_examples.txt", 'r', encoding='UTF8')
		lines = f.readlines()
		f.close()

		content = ""
		key = ""
		for i, line in enumerate(lines):
			if "###" in line:
				# 3-1. Insert the last line to list
				if i == len(lines) - 1 :  # 마지막 줄은 ###으로 끝나야 한다
					self.insert(key, content.strip())
				continue
			if "payment_template" in line:
				# 3. Insert a line to list
				if key != "":
					self.insert(key, content.strip())
					content = "" # 초기화

				# 1. Create an empty list
				line = line.strip()
				key, index = line.split(',') # index 일단 무시
				if not key in self.examples:
					self.examples[key] = []
			else:
				# 2. Make a line
				content = ''.join([content, line])

	def insert(self, key, content):
		list = self.examples[key]
		list.append(content)

class category_template():
	templates = []
	date = datetime.datetime(1970, 1, 1, 0, 0, 0) # date 없는 경우 있어서 저장해서 사용. e.g.현대카드 자동납부
	
	def __init__(self):
		# res: date, amount, payment, agent, category, memo
		self.templates.append(payment_template01) # 수기
		self.templates.append(payment_template04) # 은행, 자동납부
		self.templates.append(payment_template07)
		self.templates.append(payment_template08)
		

		self.templates.append(payment_template10) # 우리체크
		self.templates.append(payment_template11) # 우리카드

		self.templates.append(payment_template20) # 신한카드
		self.templates.append(payment_template26)
		self.templates.append(payment_template27)

		self.templates.append(payment_template30) # 현대카드
		self.templates.append(payment_template36)
		# self.templates.append(payment_template37)
		# self.templates.append(payment_template38)
		# self.templates.append(payment_template39)

	def getDate(self, dateStr):
		if len(dateStr) == 11:  # 06.29 18:00
			year = datetime.datetime.now().year
			month = int(dateStr[0:2])
			day = int(dateStr[3:5])
			hour = int(dateStr[6:8])
			min = int(dateStr[9:11])
			sec = 0
			date = datetime.datetime(year, month, day, hour, min, sec)
		elif len(dateStr) == 14: # 23.06.29 18:00
			year = int(''.join({"20", dateStr[0:2]})) # 2023
			month = int(dateStr[3:5])
			day = int(dateStr[6:8])
			hour = int(dateStr[9:11])
			min = int(dateStr[12:14])
			sec = 0
			date = datetime.datetime(year, month, day, hour, min, sec)
		elif len(dateStr) == 16: # 2023.06.29 18:00
			year = int(dateStr[0:4])
			month = int(dateStr[5:7])
			day = int(dateStr[8:10])
			hour = int(dateStr[11:13])
			min = int(dateStr[14:16])
			sec = 0
			date = datetime.datetime(year, month, day, hour, min, sec)
		else:
			try:
				date = parse(dateStr)
			except:
				date = datetime.datetime(1970, 1, 1, 0, 0, 0)
		return date
		
	# 2024.01.12 일단 날짜포맷을 이용하기 위해 여기에 추가/ 로그에 뜨는 건 USD, 엑셀에 저장은 krw 환전금액이므로 수정 필요함
	# todo:2024.03.26, krw 환산금액만 반환, 원본currency도 추가하면 좋을 듯..
	# input date는 정확함
	def getExchange(self, currency, amount, date):
		exchangeList = []
		if currency == "KRW":
			amountInKRW = int(amount.replace(',',''))
		elif currency == "CNY":
			amountInKRW = float(amount.replace(',','')) * cny * exchange_rate
		elif currency == "AUD":
			amountInKRW = float(amount.replace(',','')) * aud * exchange_rate
		elif currency == "GBP":
			amountInKRW = float(amount.replace(',','')) * gbp * exchange_rate
		elif currency == "USD":
			exchangeList = usd
		elif currency == "JPY":
			exchangeList = jpy
		else:
			amountInKRW = 999999999

		if len(exchangeList) != 0:
			if(date.strftime("%Y-%m-%d") in exchangeList.index):
				exchange_day = exchangeList[date.strftime("%Y-%m-%d")]
			else:
				while not date.strftime("%Y-%m-%d") in exchangeList.index:
					date = date - relativedelta(days=1)
				exchange_day = exchangeList[date.strftime("%Y-%m-%d")]
			amountInKRW = float(amount.replace(',','')) * exchange_day * exchange_rate
		
		result = "{:,}".format(int(round(amountInKRW)))
		#if isinstance(amountInKRW, float):
		#	result = "{:,.2f}".format(amountInKRW)
		return result
	
	# res는 template-sort순서의 list의 list
	def processData2Record(self, data, year = -1):
		res = ''

		for template in self.templates:
			regexes = []
			regexes.append(template.approval)
			regexes.append(template.cancel)

			for regex in regexes:
				searchObj = re.search(regex, data)
				if searchObj is not None:
					#print(searchObj)
					#print(':')
					#print(searchObj.group())
					#print(':')
					#print(searchObj.groups())
					#print('')
					res = template.sort(template, searchObj.groups())

					# getDate()
					if res[1] == '':
						res[1] = self.date
					else:
						res[1] = self.getDate(res[1])

					# 아래 2코드 순서, 현재 : (Data with no date) after (Data with_year) 인 경우 with_year보다 this_year가 우선
					self.date = res[1]
					if(year > 0):
						res[1] = datetime.datetime(year, res[1].month, res[1].day, res[1].hour, res[1].minute, res[1].second)

					# getExchange()
					if res[2] == '' :
						res[2] = self.getExchange(res[3][0:3], res[3][3:], res[1])

		return res

	def print_template(self):
		count_approval_cancel = 0
		for template in self.templates:
			count_approval_cancel += template.count_approval
			count_approval_cancel += template.count_cancel
		
		print(''.join(['count template matching: ', str(count_approval_cancel)]))
		for template in self.templates:
			template.print(template)

#한글(알파벳아닌)은 파이썬 버전에 따라 호환 여부 다름, 파이썬3는 유니코드 기본이라서 한글도 \w로 사용가능
##############################################################################################
class payment_template01():
	count_approval = 0
	count_cancel = 0
	payment = '수기'
	pay_method = ['출금', '입금']
	approval = r'''(출금)
((?:\d{2,4}[/ .:]){0,1}\d{2}[/ .:]\d{2}[/ .:]\d{2}[/ .:]\d{2})
(\d{1,3}(?:,?\d{3})*)(?:원){0,1}
(.*)\n?(.*)\n?(.*)'''
	cancel   = r'''(입금)
(\d{2}[/ .:]\d{2} \d{2}[/ .:]\d{2})
(\d{1,3}(?:,?\d{3})*)(?:원){0,1}
(.*)\n?(.*)\n?(.*)'''

	# as-is: approval_cancel, date, amount, agent, category, memo
	# to-be: approval_cancel, date, amountInKRW, amount, payment, agent, category, memo
	def sort(self, info_unsorted):
		list = []
		list.append(info_unsorted[0])
		list.append(info_unsorted[1])
		list.append(info_unsorted[2])
		list.append('')
		list.append(self.payment)
		list.append(info_unsorted[3])
		list.append(info_unsorted[4])
		list.append(info_unsorted[5])
		#print(list)

		if(list[0] == self.pay_method[0]):
			self.count_approval += 1
		if(list[0] == self.pay_method[1]):
			self.count_cancel += 1
		return list

	def print(self):
		res = ''.join([self.payment, ', ', self.pay_method[0], ':', str(self.count_approval), ' ', self.pay_method[1], ':', str(self.count_cancel)])
		print(res)

##############################################################################################
class payment_template08():
	count_approval = 0
	count_cancel = 0
	payment = '우리은행'
	pay_method = ['출금', '입금']
	approval = r'''\[우리은행\]
(\d{4}[.]\d{2}[.]\d{2} \d{2}:\d{2}:\d{2})
[*\-0-9]*
(.*)
(출금) (\d{1,3}(?:,\d{3})*)원\n?(.*)\n?(.*)'''
	cancel   = r'''\[우리은행\]
(\d{4}[.]\d{2}[.]\d{2} \d{2}:\d{2}:\d{2})
[*\-0-9]*
(.*)
(입금) (\d{1,3}(?:,\d{3})*)원\n?(.*)\n?(.*)'''

	# as-is: date, agent, approval_cancel, amount, category, memo
	# to-be: approval_cancel, date, amountInKRW, amount, payment, agent, category, memo
	def sort(self, info_unsorted):
		list = []
		list.append(info_unsorted[2])
		list.append(info_unsorted[0])
		list.append(info_unsorted[3])
		list.append('')
		list.append(self.payment)
		list.append(info_unsorted[1])
		list.append(info_unsorted[4])
		list.append(info_unsorted[5])
		#print(list)

		if(list[0] == self.pay_method[0]):
			self.count_approval += 1
		if(list[0] == self.pay_method[1]):
			self.count_cancel += 1
		return list

	def print(self):
		res = ''.join([self.payment, ', ', self.pay_method[0], ':', str(self.count_approval), ' ', self.pay_method[1], ':', str(self.count_cancel)])
		print(res)

##############################################################################################
class payment_template07():
	count_approval = 0
	count_cancel = 0
	payment = '신한카드 자동납부'
	pay_method = ['승인', '취소']
	approval = r'''\[신한카드\] 자동납부 정상(승인) \w\w\w님 (\d{2}/\d{2}) \(일시불\) (\d{1,3}(?:,\d{3})*)원 \b(.*)
?(.*)\n?(.*)'''
	cancel = r'''\[신한카드\] 자동납부 정상(취소) \w\w\w님 (\d{2}/\d{2}) \(일시불\) (\d{1,3}(?:,\d{3})*)원 \b(.*)
?(.*)\n?(.*)'''

	# as-is: approval_cancel, date, amount,          agent, category, memo
	# to-be: approval_cancel, date, amountInKRW, amount, payment, agent, category, memo
	def sort(self, info_unsorted):
		list = []
		list.append(info_unsorted[0])
		list.append(info_unsorted[1])
		list.append(info_unsorted[2])
		list.append('')
		list.append(self.payment)
		list.append(info_unsorted[3])
		list.append(info_unsorted[4])
		list.append(info_unsorted[5])
		#print(list)

		if(list[0] == self.pay_method[0]):
			self.count_approval += 1
		if(list[0] == self.pay_method[1]):
			self.count_cancel += 1
		return list

	def print(self):
		res = ''.join([self.payment, ', ', self.pay_method[0], ':', str(self.count_approval), ' ', self.pay_method[1], ':', str(self.count_cancel)])
		print(res)

##############################################################################################
class payment_template04():
	count_approval = 0
	count_cancel = 0
	payment = '현대카드 자동납부'
	pay_method = ['승인', '취소']
	approval = r'''\[현대카드\] 자동납부 (승인) \w\*\w님 \b(.*)\b (\d{1,3}(?:,\d{3})*)원\n?(.*)\n?(.*)'''
	cancel   = r'''\[현대카드\] 자동납부 (취소) \w\*\w님 \b(.*)\b (\d{1,3}(?:,\d{3})*)원\n?(.*)\n?(.*)'''

	# as-is: approval_cancel, agent, amount, category, memo
	# to-be: approval_cancel, date, amountInKRW, amount, payment, agent, category, memo
	def sort(self, info_unsorted):
		list = []
		list.append(info_unsorted[0])
		list.append('') # date blank
		list.append(info_unsorted[2])
		list.append('')
		list.append(self.payment)
		list.append(info_unsorted[1])
		list.append(info_unsorted[3])
		list.append(info_unsorted[4])
		#print(list)

		if(list[0] == self.pay_method[0]):
			self.count_approval += 1
		if(list[0] == self.pay_method[1]):
			self.count_cancel += 1
		return list

	def print(self):
		res = ''.join([self.payment, ', ', self.pay_method[0], ':', str(self.count_approval), ' ', self.pay_method[1], ':', str(self.count_cancel)])
		print(res)

##############################################################################################
class payment_template10():
	count_approval = 0
	count_cancel = 0
	payment = '우리체크'
	pay_method = ['승인', '취소']
	approval = r'''우리(?:카드)?\(\d\d\d\d\)체크(승인)
\w\*\w님
(\d{1,3}(?:,\d{3})*)원\s?
(\d{2}/\d{2} \d{2}:\d{2})
(.*)\n?(.*)\n?(.*)'''
	cancel = r'''우리\(\d\d\d\d\)체크(취소)
\w\*\w님
(\d{1,3}(?:,\d{3})*)원
(\d{2}/\d{2} \d{2}:\d{2})
(.*)\n?(.*)\n?(.*)'''

	# as-is: approval_cancel, amount, date, agent, category, memo
	# to-be: approval_cancel, date, amountInKRW, amount, payment, agent, category, memo
	def sort(self, info_unsorted):
		list = []
		list.append(info_unsorted[0])
		list.append(info_unsorted[2])
		list.append(info_unsorted[1])
		list.append('')
		list.append(self.payment)
		list.append(info_unsorted[3])
		list.append(info_unsorted[4])
		list.append(info_unsorted[5])
		#print(list)

		if(list[0] == self.pay_method[0]):
			self.count_approval += 1
		if(list[0] == self.pay_method[1]):
			self.count_cancel += 1
		return list

	def print(self):
		res = ''.join([self.payment, ', ', self.pay_method[0], ':', str(self.count_approval), ' ', self.pay_method[1], ':', str(self.count_cancel)])
		print(res)

##############################################################################################
class payment_template11():
	count_approval = 0
	count_cancel = 0
	payment = '우리카드'
	pay_method = ['승인', '취소']
	approval = r'''우리(?:카드)?\(\d\d\d\d\)(승인)
\w\*\w님
(\d{1,3}(?:,\d{3})*)원 .*
(\d{2}/\d{2} \d{2}:\d{2})
(.*?)
누적\d{1,3}(?:,\d{3})*원\n?(.*)\n?(.*)'''
	cancel = r'''우리(?:카드)?\(\d\d\d\d\)(취소)
\w\*\w님
(\d{1,3}(?:,\d{3})*)원\s?
(\d{1,3}(?:,\d{3})*)원 .*?
(\d{2}/\d{2} \d{2}:\d{2})

(.*)\n?(.*)\n?(.*)

(.*?)
누적\d{1,3}(?:,\d{3})*원\n?(.*)\n?(.*)'''

	# as-is: approval_cancel, amount, date, agent, category, memo
	# to-be: approval_cancel, date, amountInKRW, amount, payment, agent, category, memo
	def sort(self, info_unsorted):
		list = []
		list.append(info_unsorted[0])
		list.append(info_unsorted[2])
		list.append(info_unsorted[1])
		list.append('')
		list.append(self.payment)
		list.append(info_unsorted[3])
		list.append(info_unsorted[4])
		list.append(info_unsorted[5])
		#print(list)

		if(list[0] == self.pay_method[0]):
			self.count_approval += 1
		if(list[0] == self.pay_method[1]):
			self.count_cancel += 1
		return list

	def print(self):
		res = ''.join([self.payment, ', ', self.pay_method[0], ':', str(self.count_approval), ' ', self.pay_method[1], ':', str(self.count_cancel)])
		print(res)

##############################################################################################
class payment_template20():
	count_approval = 0
	count_cancel = 0
	payment = '신한체크'
	pay_method = ['승인', '취소']
	approval = r'''\[신한체크(승인)\] \w\*\w\(\d\d\d\d\) (\d{2}/\d{2} \d{2}:\d{2}) \(금액\)(\d{1,3}(?:,\d{3})*)원 \b(.*)\b\n?(.*)\n?(.*)'''
	cancel   = r'''\[신한체크(취소)\] \w\*\w\(\d\d\d\d\) (\d{2}/\d{2} \d{2}:\d{2}) \(금액\)(\d{1,3}(?:,\d{3})*)원 \b(.*)\b\n?(.*)\n?(.*)'''

	# as-is: approval_cancel, date, amount, agent, category, memo
	# to-be: approval_cancel, date, amountInKRW, amount, payment, agent, category, memo
	def sort(self, info_unsorted):
		list = []
		list.append(info_unsorted[0])
		list.append(info_unsorted[1])
		list.append(info_unsorted[2])
		list.append('')
		list.append(self.payment)
		list.append(info_unsorted[3])
		list.append(info_unsorted[4])
		list.append(info_unsorted[5])
		#print(list)

		if(list[0] == self.pay_method[0]):
			self.count_approval += 1
		if(list[0] == self.pay_method[1]):
			self.count_cancel += 1
		return list

	def print(self):
		res = ''.join([self.payment, ', ', self.pay_method[0], ':', str(self.count_approval), ' ', self.pay_method[1], ':', str(self.count_cancel)])
		print(res)

##############################################################################################
class payment_template26():
	count_approval = 0
	count_cancel = 0
	payment = '신한체크'
	pay_method = ['승인', '취소']
	approval = r'''신한체크해외(승인) \w\*\w\(\d\d\d\d\) (\d{2}/\d{2} \d{2}:\d{2})
KRW (\d{1,3}(?:,\d{3})*)\b(.*)\b
?(.*)\n?(.*)'''
	cancel   = r'''신한체크해외(취소) \w\*\w\(\d\d\d\d\) (\d{2}/\d{2} \d{2}:\d{2})
KRW (\d{1,3}(?:,\d{3})*)\b(.*)\b
?(.*)\n?(.*)'''
	#approval = r'''신한체크해외(승인) \w\*\w\(\d\d\d\d\) (\d{2}/\d{2} \d{2}:\d{2})\n(\d{1,3}(?:,\d{3})*\.\d{2}) 달러\b(.*)\b\n?(.*)\n?(.*)'''
	#cancel   = r'''신한체크해외(취소) \w\*\w\(\d\d\d\d\) (\d{2}/\d{2} \d{2}:\d{2})\n(\d{1,3}(?:,\d{3})*\.\d{2}) 달러\b(.*)\b\n?(.*)\n?(.*)'''
#	approval = r'''신한체크해외(승인) \w\*\w\(\d\d\d\d\) (\d{2}/\d{2} \d{2}:\d{2})
#(\d{1,3}(?:,\d{3})*\.\d{2}) 위안\b(.*)\b\n?(.*)\n?(.*)'''
#	cancel   = r'''신한체크해외(취소) \w\*\w\(\d\d\d\d\) (\d{2}/\d{2} \d{2}:\d{2})
#(\d{1,3}(?:,\d{3})*\.\d{2}) 위안\b(.*)\b\n?(.*)\n?(.*)'''

	# as-is: approval_cancel, date, amount, agent, category, memo
	# to-be: approval_cancel, date, amountInKRW, amount, payment, agent, category, memo
	def sort(self, info_unsorted):
		list = []
		list.append(info_unsorted[0])
		list.append(info_unsorted[1])
		list.append(info_unsorted[2])
		list.append('')
		list.append(self.payment)
		list.append(info_unsorted[3])
		list.append(info_unsorted[4])
		list.append(info_unsorted[5])
		#print(list)

		if(list[0] == self.pay_method[0]):
			self.count_approval += 1
		if(list[0] == self.pay_method[1]):
			self.count_cancel += 1
		return list

	def print(self):
		res = ''.join([self.payment, ', ', self.pay_method[0], ':', str(self.count_approval), ' ', self.pay_method[1], ':', str(self.count_cancel)])
		print(res)

##############################################################################################
class payment_template27():
	count_approval = 0
	count_cancel = 0
	payment = '신한체크'
	pay_method = ['승인', '취소']
	#approval = r'''신한체크해외(승인) \w\*\w\(\d\d\d\d\) (\d{2}/\d{2} \d{2}:\d{2})\n(\d{1,3}(?:,\d{3})*\.\d{2}) 달러\b(.*)\b\n?(.*)\n?(.*)'''
	#cancel   = r'''신한체크해외(취소) \w\*\w\(\d\d\d\d\) (\d{2}/\d{2} \d{2}:\d{2})\n(\d{1,3}(?:,\d{3})*\.\d{2}) 달러\b(.*)\b\n?(.*)\n?(.*)'''
	approval = r'''신한체크해외(승인) \w\*\w\(\d\d\d\d\) (\d{2}/\d{2} \d{2}:\d{2})
(\d{1,3}(?:,\d{3})*\.\d{2}) (\w{2})\b(.*)\b
?(.*)\n?(.*)'''
	cancel = r'''신한체크해외(취소) \w\*\w\(\d\d\d\d\) (\d{2}/\d{2} \d{2}:\d{2})
(\d{1,3}(?:,\d{3})*\.\d{2}) (\w{2})\b(.*)\b
?(.*)\n?(.*)'''

	# as-is: approval_cancel, date, amount, currency, agent, category, memo
	# to-be: approval_cancel, date, amountInKRW, amount, payment, agent, category, memo
	def sort(self, info_unsorted):
		if info_unsorted[3] == '달러':
			currency = 'USD'
		elif info_unsorted[3] == '위안':
			currency = 'CNY'

		list = []
		list.append(info_unsorted[0])
		list.append(info_unsorted[1])
		list.append('')
		list.append(''.join([currency, info_unsorted[2]]))  # currency + amount
		list.append(self.payment)
		list.append(info_unsorted[4])
		list.append(info_unsorted[5])
		list.append(info_unsorted[6])
		#print(list)

		if(list[0] == self.pay_method[0]):
			self.count_approval += 1
		if(list[0] == self.pay_method[1]):
			self.count_cancel += 1
		return list

	def print(self):
		res = ''.join([self.payment, ', ', self.pay_method[0], ':', str(self.count_approval), ' ', self.pay_method[1], ':', str(self.count_cancel)])
		print(res)

##############################################################################################
class payment_template30():
	count_approval = 0
	count_cancel = 0
	payment = '현대카드'
	pay_method = ['승인', '취소']
	approval = r'''현대카드 M (승인)
\w\*\w
(\d{1,3}(?:,\d{3})*)원 .*?
(\d{2}/\d{2} \d{2}:\d{2})
(.*?)
누적\d{1,3}(?:,\d{3})*원?\n?(.*)\n?(.*)'''
	cancel = r'''현대카드 M (취소)
\w\*\w
(\d{1,3}(?:,\d{3})*)원 .*?
(\d{2}/\d{2} \d{2}:\d{2})
(.*?)
누적\d{1,3}(?:,\d{3})*원?\n?(.*)\n?(.*)'''

	# as-is: approval_cancel, amount, date, agent, category, memo
	# to-be: approval_cancel, date, amountInKRW, amount, payment, agent, category, memo
	def sort(self, info_unsorted):
		list = []
		list.append(info_unsorted[0])
		list.append(info_unsorted[2])
		list.append(info_unsorted[1])
		list.append('')
		list.append(self.payment)
		list.append(info_unsorted[3])
		list.append(info_unsorted[4])
		list.append(info_unsorted[5])
		#print(list)

		if(list[0] == self.pay_method[0]):
			self.count_approval += 1
		if(list[0] == self.pay_method[1]):
			self.count_cancel += 1
		return list

	def print(self):
		res = ''.join([self.payment, ', ', self.pay_method[0], ':', str(self.count_approval), ' ', self.pay_method[1], ':', str(self.count_cancel)])
		print(res)
		
##############################################################################################
class payment_template36():
	count_approval = 0
	count_cancel = 0
	payment = '현대카드'
	pay_method = ['승인', '취소']
	approval = r'''\[현대카드\] 해외(승인)
\w\*\w님
(\d{2}/\d{2} \d{2}:\d{2})
([A-Z]{3})?\s?(\d{1,3}(?:,?\d{3})*)(?:\.\d{2})?
(.*)
?(.*)\n?(.*)'''
	cancel = r'''\[현대카드\] 해외(취소)
\w\*\w님
(\d{2}/\d{2} \d{2}:\d{2})
(\d{1,3}(?:,?\d{3})*)
(.*)
?(.*)\n?(.*)'''

	# as-is: approval_cancel, date, currency, amount, agent, category, memo
	# to-be: approval_cancel, date, amountInKRW, amount, payment, agent, category, memo
	def sort(self, info_unsorted):
		currency = info_unsorted[2]
		if currency == None:
			currency = 'KRW'
		list = []
		list.append(info_unsorted[0])
		list.append(info_unsorted[1])
		list.append('')
		list.append(''.join([currency, info_unsorted[3]]))  # currency + amount
		list.append(self.payment)
		list.append(info_unsorted[4])
		list.append(info_unsorted[5])
		list.append(info_unsorted[6])
		#print(list)

		if(list[0] == self.pay_method[0]):
			self.count_approval += 1
		if(list[0] == self.pay_method[1]):
			self.count_cancel += 1
		return list

	def print(self):
		res = ''.join([self.payment, ', ', self.pay_method[0], ':', str(self.count_approval), ' ', self.pay_method[1], ':', str(self.count_cancel)])
		print(res)
		
###############################################################################################


if __name__ == '__main__':
	categoryTemplate = category_template()

    # Example 통합
	exampleManager = example_manager()
	examples = [ #flatten
		item 
		for key, value in exampleManager.examples.items() 
		for index, item in enumerate(value)
		]
	
	keyIndex = [
		(key, index) 
		for key, value in exampleManager.examples.items() 
		for index, item in enumerate(value)
		]
	
	for i, example in enumerate(examples):
		record = categoryTemplate.processData2Record(example)
		print(keyIndex[i])
		if(record == ''):
			print(example)
		else:
			print(record)
	# end, Example 통합

	#info = categoryTemplate.processData2Record(exampleManager.examples["payment_template11"][0])
	#print(info)
	#info = categoryTemplate.processData2Record(exampleManager.examples["payment_template10"][1])
	#print(info)
	#info = categoryTemplate.processData2Record(exampleManager.examples["payment_template30"][0])
	#print(info)
	#info = categoryTemplate.processData2Record(exampleManager.examples["payment_template36"][0])
	#print(info)
	#info = categoryTemplate.processData2Record(exampleManager.examples["payment_template04"][0])
	#print(info)
	#info = categoryTemplate.processData2Record(exampleManager.examples["payment_template20"][0])
	#print(info)
	#info = categoryTemplate.processData2Record(exampleManager.examples["payment_template26"][0])
	#print(info)
	#info = categoryTemplate.processData2Record(exampleManager.examples["payment_template07"][0])
	#print(info)
	#info = categoryTemplate.processData2Record(exampleManager.examples["payment_template08"][0])
	#print(info)
	#info = categoryTemplate.processData2Record(exampleManager.examples["payment_template09"][1])
	#print(info)
	#print_template()
