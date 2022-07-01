from email.mime.text import MIMEText
from smtplib import SMTP_SSL

from libs.bolts import catch_exc, yaml_config
from libs.log import logging


@catch_exc(calc_time=True)
def send_email(content, subject, sender_show, recipient_show, to_addr, cc_show='') -> None:
    '''
    :param message: str 邮件内容
    :param subject: str 邮件主题描述
    :param sender_show: str 发件人显示，不起实际作用如："xxx"
    :param recipient_show: str 收件人显示，不起实际作用 多个收件人用','隔开如："xxx,xxxx"
    :param to_addr: str 实际收件人
    :param cc_show: str 抄送人显示，不起实际作用，多个抄送人用','隔开如："xxx,xxxx"
    '''
    if not content:
        logging.warning("email no content")
        return
    # 填写真实的发邮件服务器用户名、密码
    email_config = yaml_config('EMAIL')
    user = email_config['USERNAME']
    password = email_config['PASSWORD']
    # 邮件内容
    msg = MIMEText(content, 'html', _charset="utf-8")
    # 邮件主题描述
    msg["Subject"] = subject
    # 发件人显示，不起实际作用
    msg["from"] = sender_show
    # 收件人显示，不起实际作用
    msg["to"] = recipient_show
    # 抄送人显示，不起实际作用
    msg["Cc"] = cc_show
    with SMTP_SSL(host=email_config['HOSTNAME'], port=email_config['PORT']) as smtp:
        # 登录发送邮件服务器
        smtp.login(user=user, password=password)
        # 实际发送、接收邮件配置
        smtp.sendmail(from_addr=user, to_addrs=to_addr.split(','), msg=msg.as_string())
