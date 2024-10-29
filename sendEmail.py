import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from config import EMAIL

def send_email(subject, body, to_addresses):
    try:
        # 创建邮件对象
        msg = MIMEMultipart()
        msg['From'] = EMAIL['user']
        msg['To'] = ', '.join(to_addresses)
        msg['Subject'] = subject

        # 添加邮件正文
        msg.attach(MIMEText(body, 'plain'))

        # 连接到邮件服务器
        server = smtplib.SMTP(EMAIL['host'], EMAIL['port'])
        server.starttls()  # 启用 TLS 加密
        server.login(EMAIL['user'], EMAIL['password'])

        # 发送邮件
        server.sendmail(EMAIL['user'], to_addresses, msg.as_string())
        server.quit()

        return "邮件发送成功"
    except Exception as e:
        return "发送邮件失败: {e}"