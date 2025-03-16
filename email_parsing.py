# https://coding-kindergarten.tistory.com/210
import imaplib
import email
from pdfminer.high_level import extract_text
from io import BytesIO

# vscode에서 현재경로 문제로 인해 추가
import os
folder_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(folder_path)

class Email :
    messages = []
    
    def __init__(self, mail_address, mail_password, mail_box):
        imap = imaplib.IMAP4_SSL('imap.gmail.com')

        # imap.login('메일 주소', '비밀번호')
        imap.login(mail_address, mail_password)

        # 사서함 선택, 반환 데이터는 mailbox에 있는 메시지 수
        imap.select(mail_box)

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
            pdf_text = ""
            if email_message.is_multipart():
                for part in email_message.walk():
                    ctype = part.get_content_type()
                    cdispo = str(part.get_content_disposition()) #cdispo = str(part.get('Content-Disposition'))
                    if ctype == 'text/plain' and 'attachment' not in cdispo:
                        body = part.get_payload(decode=True)  # decode
                    # 2025.03.11 pdf 첨부파일 있으면 strings_byLine을 messages에 \n 구분해서 줄추가
                    if cdispo == "attachment":
                        filename = part.get_filename()
                        if filename:
                            # 파일 이름 디코딩
                            filename, encoding = decode_header(filename)[0]
                            if isinstance(filename, bytes):
                                filename = filename.decode(encoding or "utf-8")
                            
                            print("Attachment found:", filename)

                            # 8. PDF 내용 읽기
                            if filename.endswith(".pdf"):
                                print("Reading PDF content from memory:")
                                # 첨부파일의 바이트 데이터를 메모리에서 읽음
                                file_data = part.get_payload(decode=True)
                                pdf_stream = BytesIO(file_data)
                                pdf_text = extract_text(pdf_stream)
            else:
                body = email_message.get_payload(decode=True)
    
            # body = body.replace('\xa0', '')    # strip &nbsp
            # byte replace 하는 방법 생각중
            body = body.decode('utf-8')
            #print(body)
            
            message = '\n'.join([message, str(body)])
            if 'pdf_text' in locals() and pdf_text:  # 2025.03.11
                message = '\n'.join([message, pdf_text])
            self.messages.append(message.strip())
            
            
            
            # # 7. 첨부파일 처리
            # if email_message.is_multipart():
            #     for part in email_message.walk():
            #         # 첨부파일인지 확인
            #         if part.get_content_disposition() == "attachment":
            #             filename = part.get_filename()
            #             if filename:
            #                 # 파일 이름 디코딩
            #                 filename, encoding = decode_header(filename)[0]
            #                 if isinstance(filename, bytes):
            #                     filename = filename.decode(encoding or "utf-8")
                            
            #                 print("Attachment found:", filename)

            #                 # 8. PDF 내용 읽기
            #                 if filename.endswith(".pdf"):
            #                     print("Reading PDF content from memory:")
            #                     # 첨부파일의 바이트 데이터를 메모리에서 읽음
            #                     file_data = part.get_payload(decode=True)
            #                     pdf_stream = BytesIO(file_data)
            #                     pdf_text = extract_text(pdf_stream)
            #                     print(pdf_text)

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
    login = MailLogin()
    email_check = Email(login.mail_address, login.mail_password, login. mail_box)
