# https://coding-kindergarten.tistory.com/210
import imaplib
import email

# vscode에서 현재경로 문제로 인해 추가
import os
folder_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(folder_path)

class Email :
    messages = []
    
    def __init__(self):
        login = MailLogin()
        
        
        imap = imaplib.IMAP4_SSL('imap.gmail.com')

        # imap.login('메일 주소', '비밀번호')
        imap.login(login.mail_address, login.mail_password)

        # 사서함 선택, 반환 데이터는 mailbox에 있는 메시지 수
        imap.select(login.mail_box)

        # 사서함의 모든 메일의 uid 정보 가져오기
        # 만약 특정 발신 메일만 선택하고 싶다면 'ALL' 대신에 '(FROM "xxxxx@naver.com")' 입력
        status, messages = imap.uid('search', None, 'ALL')

        messages = messages[0].split()

        if len(messages) <= 0:
            return

        # 0이 가장 마지막 메일, -1이 가장 최신 메일
        recent_email = messages[-1]




        #print(len(messages))
        for iter_email in messages:
            message = ''
            # fetch 명령어로 메일 가져오기
            res, msg = imap.uid('fetch', iter_email, "(RFC822)")

            # 사람이 읽을 수 있는 없는 상태의 이메일
            raw = msg[0][1]

            # 사람이 읽을 수 있는 형태로 변환
            raw_readable = msg[0][1].decode('utf-8')




            # raw_readable에서 원하는 부분만 파싱하기 위해 email 모듈을 이용해 변환
            email_message = email.message_from_string(raw_readable)

            from email.header import decode_header, make_header

            # # 보낸사람
            # fr = make_header(decode_header(email_message.get('From')))
            # #print(fr)
            # message = '\n'.join([message, str(fr)])

            # # 메일 제목
            # subject = make_header(decode_header(email_message.get('Subject')))
            # #print(subject)
            # message = '\n'.join([message, str(subject)])

            # 메일 내용
            if email_message.is_multipart():
                for part in email_message.walk():
                    ctype = part.get_content_type()
                    cdispo = str(part.get('Content-Disposition'))
                    if ctype == 'text/plain' and 'attachment' not in cdispo:
                        body = part.get_payload(decode=True)  # decode
                        break
            else:
                body = email_message.get_payload(decode=True)
    
            # body = body.replace('\xa0', '')    # strip &nbsp
            # byte replace 하는 방법 생각중
            body = body.decode('utf-8')
            #print(body)
            message = '\n'.join([message, str(body)])
            self.messages.append(message.strip())

import configparser
class MailLogin :
    def __init__(self):
        config = configparser.ConfigParser() # for .ini file
        #file_user_ini = folder_path + '/user.ini'
        config.read('ledger_user.ini') # file 없으면 예외처리
        user = config['USER']
        self.mail_address = user['mail_address']
        self.mail_password = user['mail_password']
        self.mail_box = user['mail_box']


if __name__ == '__main__':
    email_check = Email()
