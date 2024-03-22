#from functools import total_ordering
import re, os

import FinanceDataReader as fdr
usd = fdr.DataReader('USD/KRW', '2018-01-01')['Close']
change_fee = 0.04

# vscode에서 현재경로 문제로 인해 추가
folder_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(folder_path)

# 2023.11.21 각 메시지_template class마다 example 변수로 관리 → class, .txt로 관리
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
				if i == len(lines) - 1 :  # 마지막 줄은 ###으로 끝나야 한다
					self.insert(key, content)
				continue
			if "payment_template" in line:
				# create pair in examples, key handling
				key_old = key
				line = line.strip()
				key, index = line.split(',') # index 일단 무시
				if not key in self.examples:
					self.examples[key] = []
				if key_old == "":
					continue

				# insert list to self.examples[key]
				self.insert(key_old, content)

				# 초기화
				content = ""
			else:
				content = ''.join([content, line])

	def insert(self, key, content):
		list = self.examples[key]
		list.append(content)

class category_template():
	templates = []
	def __init__(self):
		# res: date, amount, payment, agent, category, memo
		date = '' # date 없는 경우 있어서 저장해서 사용. e.g.현대카드 자동납부
		self.templates.append(payment_template01)
		self.templates.append(payment_template02)
		self.templates.append(payment_template03)
		self.templates.append(payment_template04)
		self.templates.append(payment_template05)
		self.templates.append(payment_template06)
		self.templates.append(payment_template07)
		self.templates.append(payment_template08)
		self.templates.append(payment_template09)
		self.templates.append(payment_template10)
		self.templates.append(payment_template11)
	
	def processData2Record(self, data):
		res = ''
		global date

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
					if res[1] == '':
						res[1] = date
					date = res[1]
					#print(date)
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
class payment_template09():
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

	# as-is: approvale_cancel, date, amount, agent, category, memo
	# to-be: approvale_cancel, date, amount, payment, agent, category, memo
	def sort(self, info_unsorted):
		list = []
		list.append(info_unsorted[0])
		list.append(info_unsorted[1])
		list.append(info_unsorted[2])
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

	# as-is: date, agent, approvale_cancel, amount, category, memo
	# to-be: approvale_cancel, date, amount, payment, agent, category, memo
	def sort(self, info_unsorted):
		list = []
		list.append(info_unsorted[2])
		list.append(info_unsorted[0])
		list.append(info_unsorted[3])
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

	# as-is: approvale_cancel, date, amount,          agent, category, memo
	# to-be: approvale_cancel, date, amount, payment, agent, category, memo
	def sort(self, info_unsorted):
		list = []
		list.append(info_unsorted[0])
		list.append(info_unsorted[1])
		list.append(info_unsorted[2])
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
class payment_template06():
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

	# as-is: approvale_cancel, date, amount, agent, category, memo
	# to-be: approvale_cancel, date, amount, payment, agent, category, memo
	def sort(self, info_unsorted):
		list = []
		list.append(info_unsorted[0])
		list.append(info_unsorted[1])
		list.append(info_unsorted[2])
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
	payment = '신한체크'
	pay_method = ['승인', '취소']
	approval = r'''신한체크해외(승인) \w\*\w\(\d\d\d\d\) (\d{2}/\d{2} \d{2}:\d{2})\n(\d{1,3}(?:,\d{3})*\.\d{2}) 달러\b(.*)\b\n?(.*)\n?(.*)'''
	cancel   = r'''신한체크해외(취소) \w\*\w\(\d\d\d\d\) (\d{2}/\d{2} \d{2}:\d{2})\n(\d{1,3}(?:,\d{3})*\.\d{2}) 달러\b(.*)\b\n?(.*)\n?(.*)'''

	# as-is: approvale_cancel, date, amount, agent, category, memo
	# to-be: approvale_cancel, date, amount, payment, agent, category, memo
	def sort(self, info_unsorted):
		list = []
		list.append(info_unsorted[0])
		list.append(info_unsorted[1])
		list.append(info_unsorted[2])
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
class payment_template05():
	count_approval = 0
	count_cancel = 0
	payment = '신한체크'
	pay_method = ['승인', '취소']
	approval = r'''\[신한체크(승인)\] \w\*\w\(\d\d\d\d\) (\d{2}/\d{2} \d{2}:\d{2}) \(금액\)(\d{1,3}(?:,\d{3})*)원 \b(.*)\b\n?(.*)\n?(.*)'''
	cancel   = r'''\[신한체크(취소)\] \w\*\w\(\d\d\d\d\) (\d{2}/\d{2} \d{2}:\d{2}) \(금액\)(\d{1,3}(?:,\d{3})*)원 \b(.*)\b\n?(.*)\n?(.*)'''

	# as-is: approvale_cancel, date, amount, agent, category, memo
	# to-be: approvale_cancel, date, amount, payment, agent, category, memo
	def sort(self, info_unsorted):
		list = []
		list.append(info_unsorted[0])
		list.append(info_unsorted[1])
		list.append(info_unsorted[2])
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

	# as-is: approvale_cancel, agent, amount, category, memo
	# to-be: approvale_cancel, date, amount, payment, agent, category, memo
	def sort(self, info_unsorted):
		list = []
		list.append(info_unsorted[0])
		list.append('') # date blank
		list.append(info_unsorted[2])
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
class payment_template03():
	count_approval = 0
	count_cancel = 0
	payment = '현대카드'
	pay_method = ['승인', '취소']
	approval = r'''\[현대카드\] 해외(승인)
\w\*\w님
(\d{2}/\d{2} \d{2}:\d{2})
(?:KRW\s)?(\d{1,3}(?:,?\d{3})*)(?:\.\d{2})?
(.*?)
(.*)\n?(.*)'''
	cancel = r'''\[현대카드\] 해외(취소)
\w\*\w님
(\d{2}/\d{2} \d{2}:\d{2})
(\d{1,3}(?:,?\d{3})*)
(.*?)
(.*)\n?(.*)'''

	# as-is: approvale_cancel, date, amount, agent, category, memo
	# to-be: approvale_cancel, date, amount, payment, agent, category, memo
	def sort(self, info_unsorted):
		list = []
		list.append(info_unsorted[0])
		list.append(info_unsorted[1])
		list.append(info_unsorted[2])
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
class payment_template10():
	count_approval = 0
	count_cancel = 0
	payment = '현대카드'
	pay_method = ['승인', '취소']
	approval = r'''\[현대카드\] 해외(승인)
\w\*\w님
(\d{2}/\d{2} \d{2}:\d{2})
USD (\d{1,3}(?:,?\d{3})*\.\d{2})
(.*?)
(.*)\n?(.*)'''
	cancel = r'''\[현대카드\] 해외(취소)
\w\*\w님
(\d{2}/\d{2} \d{2}:\d{2})
USD (\d{1,3}(?:,?\d{3})*\.\d{2})
(.*?)
(.*)\n?(.*)'''

	# as-is: approvale_cancel, date, amount, agent, category, memo
	# to-be: approvale_cancel, date, amount, payment, agent, category, memo
	def sort(self, info_unsorted):
		list = []
		list.append(info_unsorted[0])
		list.append(info_unsorted[1])
		list.append(info_unsorted[2])
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
class payment_template02():
	count_approval = 0
	count_cancel = 0
	payment = '현대카드'
	pay_method = ['승인', '취소']
	approval = r'''현대카드 M (승인)
\w\*\w
(\d{1,3}(?:,\d{3})*)원 .*?
(\d{2}/\d{2} \d{2}:\d{2})
(.*?)
누적\d{1,3}(?:,\d{3})*원\n?(.*)\n?(.*)'''
	cancel = r'''현대카드 M (취소)
\w\*\w
(\d{1,3}(?:,\d{3})*)원 .*?
(\d{2}/\d{2} \d{2}:\d{2})
(.*?)
누적\d{1,3}(?:,\d{3})*원\n?(.*)\n?(.*)'''

	# as-is: approvale_cancel, amount, date, agent, category, memo
	# to-be: approvale_cancel, date, amount, payment, agent, category, memo
	def sort(self, info_unsorted):
		list = []
		list.append(info_unsorted[0])
		list.append(info_unsorted[2])
		list.append(info_unsorted[1])
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
class payment_template01():
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

	# as-is: approvale_cancel, amount, date, agent, category, memo
	# to-be: approvale_cancel, date, amount, payment, agent, category, memo
	def sort(self, info_unsorted):
		list = []
		list.append(info_unsorted[0])
		list.append(info_unsorted[2])
		list.append(info_unsorted[1])
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


if __name__ == '__main__':
	categoryTemplate = category_template()

	exampleManager = example_manager()
	examples = [item for key, value in exampleManager.examples.items() for index, item in enumerate(value)]
	
	keyIndex = [(key, index) for key, value in exampleManager.examples.items() for index, item in enumerate(value)]
	for i, example in enumerate(examples):
		info = categoryTemplate.processData2Record(example)
		print(keyIndex[i])
		if(info == ''):
			print(example)
		else:
			print(info)

	#info = categoryTemplate.processData2Record(exampleManager.examples["payment_template01"][1])
	#print(info)
	#info = categoryTemplate.processData2Record(exampleManager.examples["payment_template02"][0])
	#print(info)
	#info = categoryTemplate.processData2Record(exampleManager.examples["payment_template03"][0])
	#print(info)
	#info = categoryTemplate.processData2Record(exampleManager.examples["payment_template04"][0])
	#print(info)
	#info = categoryTemplate.processData2Record(exampleManager.examples["payment_template05"][0])
	#print(info)
	#info = categoryTemplate.processData2Record(exampleManager.examples["payment_template06"][0])
	#print(info)
	#info = categoryTemplate.processData2Record(exampleManager.examples["payment_template07"][0])
	#print(info)
	#info = categoryTemplate.processData2Record(exampleManager.examples["payment_template08"][0])
	#print(info)
	#info = categoryTemplate.processData2Record(exampleManager.examples["payment_template09"][1])
	#print(info)
	#print_template()