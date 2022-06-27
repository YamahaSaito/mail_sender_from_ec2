#
# usage: $ python3 mailtest.py
#

import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

from datetime import datetime
from dataclasses import dataclass, asdict
from glob import glob
import logging
import os
from pathlib import Path
import sys
from typing import Tuple


from PIL import Image
import yaml


CURRENTDIR = Path(__file__).parent.resolve()
sys.path.insert(1, str(CURRENTDIR))

logger = logging.getLogger("logger_mail")

from error_handler import DeliverablesException


PARAM_PATH = str(CURRENTDIR / "config" / "smtp_config.yaml")


@dataclass(frozen=True)
class SmtpParam():
    """SendSmtpクラスのコンフィグデータです。
    連続して複数のメールサーバー、送信元、送信先にメールを送れるよう、
    SMTP_SERVER/SMTP_PORT/MAILLIST/NEED_AUTHはリスト形式になっています。

    Raises:
        DeliverablesException.Else: [description]
    """
    SMTP_SERVER   : list
    SMTP_PORT     : list
    MAILLIST      : dict
    RUN_UI_PATH   : str
    NEED_AUTH     : list
    DEBUG_FLG     : bool
    TEXT_STRS     : dict

    def _post_init_(self):

        user_dict = asdict(self)
        for user_arg_name, user_arg_expected_type in self._annotations_.items():

            if not isinstance(user_dict[user_arg_name], user_arg_expected_type):
                logger.error('{%s} is type error' %user_arg_name)
                raise DeliverablesException.Else('{%s} is type error' %user_arg_name)

class SendSmtp():
    """AIピッキングプラットフォームでSMTPプロトコルでメールを送信するためのクラス
    """
    def __init__(self):
        """
        Raises:
            DeliverablesException.Else: コンフィグファイルが存在しない、もしくはパスが間違っている場合はエラー発生
        """
        if not os.path.exists(str(PARAM_PATH)):
            raise DeliverablesException.Else("param fle is not exist: %s" %PARAM_PATH)
        self._PARAM = SmtpParam(**yaml.safe_load(open(PARAM_PATH,"r")))

    def send_mail(self, attachment_fles: list, state: str="start", ui_mode: str ="run_ui")-> bool:
        """[summary]

        Args:
            state (str, optional): [description]. Defaults to "start".
            msg (str, optional): [description]. Defaults to "".
            job_result_dir ([type], optional): [description]. Defaults to None.
            ui_mode (str, optional): [description]. Defaults to "run_ui".

        Returns:
            bool: 送信に成功した場合はTrueを,そうでない場合はFalseを返す.
        """
        logger.debug("entered send_mail process")
        
        from_addrs       = self._PARAM.MAILLIST["from_addr"]
        to_addrs         = self._PARAM.MAILLIST["to_addr"]

        logger.debug("get mail subject and text")
        str_subject, str_msg = self._get_mailtext(state, ui_mode)
        logger.info("mail subject: %s, mail text: %s" %(str_subject, str_msg))

        attachment_files = []
        for fle in attachment_fles:
            attachment_files = self._get_attached_obj(fle, attachment_files)

        logger.debug("start attaching text")
        for idx in range(len(from_addrs)):
            if not self._PARAM.DEBUG_FLG:
                logger.debug("try to get smtp object")
                self._get_smtp_obj(idx)

                logger.debug("start sending")
                mailpart = self._create_mailpart(subject=str_subject, from_addrs=from_addrs[idx], to_addrs=to_addrs[idx], msg=str_msg, attachment_files=attachment_files)

                _ = self._send_mail_obj(from_addrs=from_addrs[idx], to_addrs=to_addrs[idx], mailpart=mailpart)
        return ret

    def _create_mailpart(self, subject: str, from_addrs: str, to_addrs: str, msg: str, attachment_files: list)-> MIMEMultipart:
        mailpart = MIMEMultipart()
        mailpart['Subject'] = subject
        mailpart['From']    = from_addrs
        mailpart['To']      = to_addrs
        mailpart['Date']    = formatdate()

        mailpart.attach(MIMEText(msg))

        logger.debug("start attaching attachments")
        for fle in attachment_files:
            mailpart.attach(fle)
        return mailpart

    def _get_attached_obj(self, fle: str, attachment_fles: list)-> list:
        logger.debug("fle: %s" %fle)
        extension = fle.rsplit(".",1)[-1]
        if extension in ["jpg", "png", "bmp", "tiff"]:
            with open(fle, "rb") as f:
                attachment_fle = MIMEImage(f.read(), _subtype=extension)
        elif (extension in ["log", "txt"]) or ("log" in fle):
            with open(fle, "r") as f:
                attachment_fle = MIMEText(f.read())
            if (extension not in ["log", "txt"]) and ("log" in fle):
                fle = fle + ".log"
        else:
            raise DeliverablesException.Code3()
        attachment_fle.set_param('name',fle.rsplit("/",1)[-1])
        attachment_fle.add_header('Content-Disposition','attachment',filename=fle.rsplit("/",1)[-1])
        attachment_fles.append(attachment_fle)
        logger.debug("file is successfully attached")
        return attachment_fles

    def _get_mailtext(self, state: str, msg: str, ui_mode: str)-> Tuple[str, str]:
        """This function is to get the suitable subject and message for each ai picking system state.

        Args:
            state (str): The state of the ai picking system. Has to be chosen from ["start", "error", done"]
            msg (str): The message from ai picking system. If status is start, this should be "".

        Returns:
            str_subject [str]: The subject of the e-mail to be sent.
            str_msg [str]: The message of the e-mail to be sent.
        """
        if state in ["error", "start", "done"]:
            str_subject = str(self._PARAM.TEXT_STRS[ui_mode][state]["subject"]) + datetime.now().strftime("%Y/%m/%d %H:%M")
            str_msg     = str(self._PARAM.TEXT_STRS[ui_mode][state]["msg"])
            if msg is not None:
                str_msg = str_msg + "\n{}".format(msg)
        else:
            raise Exception("state: %s in not in the list of [error, start, done]" %state)
        return str_subject, str_msg

    def _get_smtp_obj(self, idx: int):
        """SMTPオブジェクトを生成し、通信を確立するメソッド.
        送信するメールアカウントに認証が必要な場合、コンフィグファイルのNEED_AUTHをTrueにする.
        2段階認証が必要な場合、当SMTPプロトコルでは送信できないため別のアカウントを使用すること

        Args:
            idx (int): 送信するSMTP_SERVERなどに対応するインデックス

        Raises:
            DeliverablesException.Code3: [description]
        """
        try:
            self.smtpobj = smtplib.SMTP(self._PARAM.SMTP_SERVER[idx], self._PARAM.SMTP_PORT[idx])
            if self._PARAM.NEED_AUTH[idx]:
                logger.debug("Authentication is needed")
                self.smtpobj.starttls()
                self.smtpobj.login(self._PARAM.MAILLIST["from_addr"][idx], self._PARAM.MAILLIST["password"][idx])
        except:
            raise DeliverablesException.Code3()

    def _send_mail_obj(self, from_addrs: str, to_addrs: str, mailpart: MIMEMultipart)-> bool:
        try:
            self.smtpobj.sendmail(from_addrs, to_addrs.split(","), mailpart.as_string())
            ret = True
        except OSError as ERR:
            print(str(ERR))
            raise DeliverablesException.Code3()
        finally:
            self.smtpobj.quit()
            logger.debug("exit send_mail process")
            ret = False
        return ret


if __name__=="__main__":

    mes = "This is test!!"

    print("start mail process")
 
    sndsmtp = SendSmtp()
    for i in range(1):
        print("got smtp_object")
        ret = sndsmtp.send_mail(state="start", msg=mes, job_result_dir=None)
        print("got smtp_object")
        #ret = sndsmtp.send_mail(state="error", msg=mes,
        #     job_result_dir=Path('/media/aipicking/5bf0ff55-5dba-4309-8b61-bd3dcfdaa739/results_SHIBAHARA/run_results/2021-11-18_19:30:32'))
        print("got smtp_object")
        #ret = sndsmtp.send_mail(state="done", msg=mes,
        #     job_result_dir=Path('/media/aipicking/5bf0ff55-5dba-4309-8b61-bd3dcfdaa739/results_SHIBAHARA/run_results/2021-11-18_19:30:32'))
        print(ret)

#https://qiita.com/siida36/items/be21d361cf80d664859c
#aipicking@ubuntu:~/AiPick/fujitaha_mailtest$ sudo ufw status
#状態: 非アクティブ
#aipicking@ubuntu:~/AiPick/fujitaha_mailtest$ sudo ufw allow 25
#ルールをアップデートしました
#ルールをアップデートしました(v6)
#aipicking@ubuntu:~/AiPick/fujitaha_mailtest$ sudo ufw reload
#ファイアウォールは有効になっていません（再読込を飛ばします）
#aipicking@ubuntu:~/AiPick/fujitaha_mailtest$ sudo ufw enable
#ファイアウォールはアクティブかつシステムの起動時に有効化されます。
#aipicking@ubuntu:~/AiPick/fujitaha_mailtest$ sudo ufw reload
#ファイアウォールを再読込しました
#aipicking@ubuntu:~/AiPick/fujitaha_mailtest$ sudo ufw status
#状態: アクティブ

#To                         Action      From
#--                         ------      ----
#25                         ALLOW       Anywhere                  
#25 (v6)                    ALLOW       Anywhere (v6)

#http://thalion.hatenablog.com/entry/20090622/p1
   
