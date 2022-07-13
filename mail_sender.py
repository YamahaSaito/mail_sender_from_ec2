from asyncio.log import logger
from email.mime.text import MIMEText
from email.utils import formatdate
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import smtplib

from abc import abstractmethod, ABCMeta
from datetime import datetime
from dataclasses import dataclass, asdict
from glob import glob
import logging
import os
from pathlib import Path
import subprocess
import time
from typing import Tuple


import yaml


from logger_configurator import configure_logger


CURRENTDIR                    = Path(__file__).resolve().parent
MAIL_SENDER_CONFIG_PATH       = str(CURRENTDIR / "config" / "smtp_config.yaml")
CLOUD_STRAGE_CONFIG_PATH      = str(CURRENTDIR / "config" / "cloud_strage_config.yaml")
LOCAL_STRAGE_CONFIG_PATH      = str(CURRENTDIR / "config" / "local_strage_config.yaml")
MAIL_RECORD_PATH              = str(CURRENTDIR / "config" / "mail_record.yaml")
LOGGER_CONFIG_PATH            = str(CURRENTDIR / "config" / "log_conf" / "logger_config.yaml")

@dataclass(frozen=True)
class SmtpParams():
    """SendSmtpクラスのコンフィグデータです。
    連続して複数のメールサーバー、送信元、送信先にメールを送れるよう、
    SMTP_SERVER/SMTP_PORT/MAILLIST/NEED_AUTHはリスト形式になっています。

    Raises:
        DeliverablesException.Else: [description]
    """
    SMTP_SERVER      : list
    SMTP_PORT        : list
    MAILLIST         : dict
    RUN_UI_PATH      : str
    NEED_AUTH        : list
    DEBUG_FLG        : bool
    TEXT_STRS        : dict
    MAIL_STATUS_LIST : list
    UI_MODE_LIST     : list
    SEND_MAIL_KEYWORD: str

    def _post_init_(self):

        user_dict = asdict(self)
        for user_arg_name, user_arg_expected_type in self._annotations_.items():

            if not isinstance(user_dict[user_arg_name], user_arg_expected_type):
                logger.error('{%s} is type error' %user_arg_name)
                raise ValueError('{%s} is type error' %user_arg_name)


@dataclass(frozen=True)
class StrageParams():
    """SendSmtpクラスのコンフィグデータです。
    連続して複数のメールサーバー、送信元、送信先にメールを送れるよう、
    SMTP_SERVER/SMTP_PORT/MAILLIST/NEED_AUTHはリスト形式になっています。

    Raises:
        DeliverablesException.Else: [description]
    """
    ROOT_DIR                : str
    LATEST_LOG_PATH         : str
    LATEST_STATUS_LINE      : str
    TIME_FORMAT             : str
    FILE_TIME_STR           : str # "%Y-%m-%d_%H:%M:%S"

    def _post_init_(self):

        user_dict = asdict(self)
        for user_arg_name, user_arg_expected_type in self._annotations_.items():

            if not isinstance(user_dict[user_arg_name], user_arg_expected_type):
                logger.error('{%s} is type error' %user_arg_name)
                raise ValueError('{%s} is type error' %user_arg_name)


class MailSender(metaclass=ABCMeta):
    @abstractmethod
    def _configure_logger(self, logger_config_path: str, save_root_dir: str)-> logging.Logger:
        pass

    @abstractmethod
    def _fetch_attachment_lst(self, job_dir: str, log_path: str, status: str)-> list:
        pass

    @abstractmethod
    def _get_img_lst4done(self, job_dir: str)-> list:
        pass

    @abstractmethod
    def _get_latest_dir(self)-> str:
        pass

    @abstractmethod
    def _get_latest_log_path(self, job_dir: str)-> str:
        pass

    @abstractmethod
    def _get_modified_time(self, path: str, is_file: bool)-> datetime:
        pass

    @abstractmethod
    def _search(self, search_dir: str, is_file: bool=False)-> list:
        pass

    @abstractmethod
    def _send(self, log_path: str, job_dir: str, status: str, ui_mode: str, config: dict)-> bool:
        pass

    def _check_status_is_not_sent(self, log_path: str, line_no: int, last_mail_config: dict)-> bool:
        """This method is to check the mail needs to be sent at this current situation.
        As whether send the mail or not is decided by checking non-syncronized log file, it is possible to re-send exactly same error massage.
        To prevent such situation, we record the log file and line number of the mail status in log file,
        and check if the current log file is differ from last log file or current line number is larger than last line number.

        Args:
            log_path (str): The current (which is equal to the latest) log file path. Must be absolute path.
            line_no (int): The line number of the current mail status found in the current log file.
            last_mail_config (dict): The config dict which contain the log file path and line number of the last mail sending process.

        Returns:
            bool: Return True if the current mail status or line number is new (which means mail have to be sent). If not, return False
        """
        self._logger.debug("[Checkpoint] enter _check_status_is_not_sent")

        res = False
        self._logger.debug("[Variables]  res: %s" %res)

        last_log_record = last_mail_config["log_path"]
        last_log_lineno = last_mail_config["line_no"]
        self._logger.debug("[Variables]  log_path: %s" %log_path)
        self._logger.debug("[Variables]  line_no: %s" %line_no)
        self._logger.debug("[Variables]  last_log_record: %s" %last_log_record)
        self._logger.debug("[Variables]  last_log_lineno: %s" %last_log_lineno)

        self._logger.debug("[BranchPoint]  log_path != last_log_record: %s" %(log_path != last_log_record))
        self._logger.debug("[BranchPoint]  (log_path == last_log_record) and (line_no > last_log_lineno): %s" %((log_path == last_log_record) and (line_no > last_log_lineno)))
        if (log_path != last_log_record):
            res = True
        elif ((log_path == last_log_record) and (line_no > last_log_lineno)):
            res = True
        else:
            res = False
        self._logger.debug("[Variables]  res: %s" %res)

        self._logger.debug("[Checkpoint] exit _check_status_is_not_sent")
        return res

    def _create_mailpart(self, subject: str, from_addrs: str, to_addrs: str, msg: str, attachments: list)-> MIMEMultipart:
        """This method create the essential part to send email, which is the subject, from and to addresses, message text, and attachment files of the mail tp be sent.
        This could be done between creating smtp object and send them. However in poor networking situation, the smtp object canbe easily lostbefore send them.
        Inorder to prevent those fatal error, we suggest u to call this method before creating smtp object.

        Args:
            subject (str): The subject of the email to be sent.
            from_addrs (str): The email address of the sender. This address must be single email address.
            to_addrs (str): The email address of the reciever. This addresses could be multiple email address. To send multiple recievers, connect email address with "," and enter as the single string.
            msg (str): The message of the email to be sent.
            attachments (list): The list of attachment files in the format of MIMEText if the attachment is text file, or MIMEImage if the attachment is image file, otherwise it is not accrotable extension format.

        Returns:
            MIMEMultipart: Returns main part of email to be sent in the format of MIMEMultipart.
        """
        self._logger.debug("[Checkpoint] enter _create_mailpart")

        self._logger.debug("[Variables]  subject: %s" %subject)
        self._logger.debug("[Variables]  from_addrs: %s" %from_addrs)
        self._logger.debug("[Variables]  to_addrs: %s" %to_addrs)
        self._logger.debug("[Variables]  formatdate(): %s" %formatdate())
        self._logger.debug("[Variables]  msg: %s" %msg)

        mailpart = MIMEMultipart()
        mailpart["Subject"] = subject
        mailpart["From"]    = from_addrs
        mailpart["To"]      = to_addrs
        mailpart["Date"]    = formatdate()
        mailpart.attach(MIMEText(msg))

        self._logger.debug("[Variables]  attachments: %s" %attachments)
        for attachment in attachments:
            mailpart.attach(attachment)

        self._logger.debug("[Checkpoint] exit _create_mailpart")
        return mailpart

    def _get_attachment(self, fle_path: str, attachments: list)-> list:
        """This method formats the attachement file path list to the list of the object with the suitable emailing formats.

        Args:
            fle_path (str): THe absolute path of the attachment file. The accteptable extension format is [".log", ".txt"] for text files and [".jpg", ".png", ".bmp", ".tiff"] for image files.
            attachments (list): The list of the attachment object in the suitable emailing format. In the initial condition, this is empty list.

        Returns:
            list: The list of the attachment object in the suitable emailing format. This list stores attachment object as this method is repeatedly called.
        """
        self._logger.debug("[Checkpoint] enter _get_attachment")
        self._logger.debug('[Variables]  attachments: %s' %attachments)

        extension = fle_path.rsplit(".", 1)[-1]
        self._logger.debug("[Variables]  extension: %s" %extension)

        self._logger.debug('[BranchPoint]  extension in ["jpg", "png", "tiff", "bmp"]: %s' %(extension in ["jpg", "png", "tiff", "bmp"]))
        self._logger.debug('[BranchPoint]  (extension in ["log", "txt"]) or ("log" in fle_path): %s' %((extension in ["log", "txt"]) or ("log" in fle_path)))
        if extension in ["jpg", "png", "tiff", "bmp"]:
            with open(fle_path, "rb") as f:
                attachment_obj = MIMEImage(f.read(), _subtype=extension)
        elif ((extension in ["log", "txt"]) or ("log" in fle_path)):
            with open(fle_path, "r") as f:
                attachment_obj = MIMEText(f.read())
            self._logger.debug('[BranchPoint]  (extension not in ["log", "txt"]) and ("log" in fle_path): %s' %((extension not in ["log", "txt"]) and ("log" in fle_path)))
            if ((extension not in ["log", "txt"]) and ("log" in fle_path)):
                fle_path = fle_path + ".log"

        self._logger.debug('[Variables]  fle_path.rsplit("/", 1)[-1]: %s' %fle_path.rsplit("/", 1)[-1])
        attachment_obj.set_param("name", fle_path.rsplit("/", 1)[-1])
        attachment_obj.add_header("Content-Disposition", "attachment", filename=fle_path.rsplit("/", 1)[-1])

        attachments.append(attachment_obj)
        self._logger.debug('[Variables]  attachments: %s' %attachments)

        self._logger.debug("[Checkpoint] exit _get_attachment")
        return attachments

    def _get_mail_status(self, log_path: str)->Tuple[str, str, int]:
        """This method gets the current mail status and corresponding message from the current log file.
        The searching is processed from last to begin of the log file as latest status is needed.

        Args:
            log_path (str): The path of the current log file. this could be both absolute and relative path.

        Returns:
            status (str): The current status of the mail to be sent.
            msg (str): The message correspond to the current email status.
            line_no (int): The line number of the line where the current status found in current log file. 
        """
        self._logger.debug("[Checkpoint] enter _get_mail_status")

        self._logger.debug('[Variables]  log_path: %s' %log_path)
        with open(log_path, "r") as f:
            log_txt_lst = f.read().split("\n")[:-1]
        self._logger.debug('[Variables]  log_txt_lst: %s' %log_txt_lst)

        status = "none"
        msg    = "none"

        for i in range(len(log_txt_lst)):
            line_no = len(log_txt_lst) - (i + 1)
            self._logger.debug('[Variables]  line_no: %s' %line_no)

            self._logger.debug('[Variables]  log_txt_lst[line_no]: %s' %log_txt_lst[line_no])
            # self._logger.debug('[BranchPoint]  "[MailStatus]" in log_txt_lst[line_no]: %s' %("[MailStatus]" in log_txt_lst[line_no]))
            if self._mail_keywd in log_txt_lst[line_no]:  # mail status is recorded in log file in the format of "[MailStatus], Status :%status, Msg :%msg"
                # _, status_txt, msg_txt = log_txt_lst.rsplit(",", 2)
                # self._logger.debug('[Variables]  status_txt: %s' %status_txt)
                # self._logger.debug('[Variables]  msg_txt: %s' %msg_txt)

                # status = status_txt.split(":", 1)[-1]
                # msg    = msg_txt.split(":", 1)[-1]
                # self._logger.debug('[Variables]  status: %s' %status)
                # self._logger.debug('[Variables]  msg: %s' %msg)
                status = "error"
                msg = "test"
                break

        self._logger.debug('[Variables]  line_no: %s' %line_no)
        self._logger.debug("[Checkpoint] exit _get_mail_status")
        return status, msg, line_no

    def _get_mail_config(self, config: SmtpParams):
        self._logger.debug("[Checkpoint] enter _get_mail_config")
        self._smtp_server     = config.SMTP_SERVER
        self._smtp_port       = config.SMTP_PORT
        self._to_addrs        = config.MAILLIST["to_addr"]
        self._from_addrs      = config.MAILLIST["from_addr"]
        self._maillist        = config.MAILLIST
        self._need_auth       = config.NEED_AUTH
        self._debug_flg       = config.DEBUG_FLG
        self._text_strs       = config.TEXT_STRS
        self._mail_status_lst = config.MAIL_STATUS_LIST
        self._mail_ui_modes   = config.UI_MODE_LIST
        self._mail_keywd      = config.SEND_MAIL_KEYWORD
        self._logger.debug("[Checkpoint] exit _get_mail_config")

    def _get_mailtext(self, status: str, ui_mode: str, msg: str=None)-> Tuple[str, str]:
        """This method returns the suitable subject and message format for the current email status and ui modes.

        Args:
            status (str): The current status of the mail to be sent.
            ui_mode (str): The current ui mode,as the email subject could differ for each ui mode.
            msg (str, optional): The message correspond to the current email status. If no message is defined, The formatted message will be added anyway. Defaults to None.

        Raises:
            ValueError: If input email status is not valid, raise ValueError.
            ValueError: If input ui mode is not valid, raise ValueError.

        Returns:
            Tuple[str, str]: Returns strings of the subject and message text of the email.
        """
        self._logger.debug("[Checkpoint] enter _get_mailtext")
        self._logger.debug('[Variables]  status: %s' %status)
        self._logger.debug('[Variables]  ui_mode: %s' %ui_mode)
        self._logger.debug('[Variables]  msg: %s' %msg)

        self._logger.debug('[BranchPoint]  status not in self._mail_status_lst: %s' %(status not in self._mail_status_lst))
        self._logger.debug('[BranchPoint]  ui_mode not in self._mail_ui_modes: %s' %(ui_mode not in self._mail_ui_modes))
        if status not in self._mail_status_lst:
            raise ValueError(f"status: {status} is not acceptable value. Status must be in [{self._mail_status_lst}]")
        elif ui_mode not in self._mail_ui_modes:
            raise ValueError(f"status: {ui_mode} is not acceptable value. UI_mode must be in [{self._mail_ui_modes}]")
        else:
            str_subject = str(self._text_strs[ui_mode][status]["subject"])
            str_msg     = str(self._text_strs[ui_mode][status]["msg"])
            if msg != None:
                str_msg = f"{str_msg}\n{msg}"

        self._logger.debug('[Variables]  str_subject: %s' %str_subject)
        self._logger.debug('[Variables]  str_msg: %s' %str_msg)
        self._logger.debug("[Checkpoint] exit _get_mailtext")
        return str_subject, str_msg

    def _get_ui_mode(self, job_dir: str)-> str:
        """This method is to get the ui mode of the current log file form absolute oath of the log file.

        Args:
            job_dir (str): The directory path which contain current log file path.

        Returns:
            str: Returns ui mode. This must be in the list of ["run_ui", "train_ui", "pickuptest_ui"].
        """
        self._logger.debug("[Checkpoint] enter _get_ui_mode")
        self._logger.debug('[Variables]  job_dir: %s' %job_dir)

        _, ui_mode, _, _ = job_dir.rsplit("/", 3)
        self._logger.debug('[Variables]  ui_mode: %s' %ui_mode)
        self._logger.debug("[Checkpoint] exit _get_ui_mode")
        return ui_mode

    def _send_smtpobj(self, smtp_server: str, smtp_port: str, from_addrs: str, to_addrs: str, passwd: str, need_auth: bool, mailpart: MIMEMultipart)-> bool:
        """This method gets smtp object and send that object.

        Args:
            smtp_server (str): The string of the smtp server ip address. This could be different for which mail domain and provider ur mail sender address uses.
            smtp_port (str): The string of the smtp server port number. This could be different for which mail domain and provider ur mail sender address uses. Usually 80.
            from_addrs (str): The email address of the sender. This must be single email address as smtp could not send from multiple sender address.
            to_addrs (str): The email addresses of the recievers. This could be mnultiple email addresses. In this case, join the reciver email addresses with ",", and inout as the single tring.
            passwd (str): The password of the sender email account. This will be needed if the seder email provider requires authentification.
            need_auth (bool): True if the sender email provider requires authentification to send by smtp protocols. If the provider requires double-authentification, consider to use another email provider as double-authentification is not implemented in smtp protocols and never will be.
            mailpart (MIMEMultipart): The main part of the email to be sent in the format of MIMEMultipart.

        Raises:
            ValueError: Raise ValueError if the smtp object could not be created or authetification failed.
            ValueError: Raise ValueError if the smtp object unsuccessfully send.

        Returns:
            ret [bool]: Returns True if send process successed. If this process unsuccessed, reutrns False.
        """
        self._logger.debug("[Checkpoint] enter _send_smtpobj")

        self._logger.debug('[Variables]  smtp_server: %s' %smtp_server)
        self._logger.debug('[Variables]  smtp_port: %s' %smtp_port)
        self._logger.debug('[Variables]  from_addrs: %s' %from_addrs)
        self._logger.debug('[Variables]  to_addrs: %s' %to_addrs)
        self._logger.debug('[Variables]  passwd: %s' %passwd)
        self._logger.debug('[Variables]  need_auth: %s' %need_auth)
        self._logger.debug('[Variables]  mailpart: %s' %mailpart)

        try:
            self._smtpobj = smtplib.SMTP(smtp_server, smtp_port)
            if need_auth:
                self._smtpobj.starttls()
                self._smtpobj.login(from_addrs, passwd)
        except:
            raise ValueError("Failed to create smtp object. Please check the mail address, smtp server and port, password, and authentification are correct")

        try:
            self._smtpobj.sendmail(from_addrs, to_addrs.split(","), mailpart.as_string())
            ret = True
        except OSError as ERR:
            ret = False
            raise ValueError(ERR)
        finally:
            self._smtpobj.close()
            self._logger.debug('[Variables]  ret: %s' %ret)
            self._logger.debug("[Checkpoint] exit _send_smtpobj")
            return ret

    def _set_logger(self, logger: logging.Logger):
        self._logger = logger

    def _save_mail_status(self, config: dict, config_path: str)-> bool:
        self._logger.debug("[Checkpoint] enter _save_mail_status")

        self._logger.debug('[Variables]  config: %s' %config)
        self._logger.debug('[Variables]  config_path: %s' %config_path)

        config_path = Path(config_path)
        if not os.path.exists(str(config_path)):
            os.makedirs(str(config_path.parent), exist_ok=True)
        with open(str(config_path), "w+") as f:
            yaml.safe_dump(config, f)
        self._logger.debug("[Checkpoint] exit _save_mail_status")
        return True


class MailSender4ec2(MailSender):
    """This class is to send email through the ec2 instance and data stored in s3 container.

    Args:
        MailSender (ABCMeta): The abstract class of the mail sender class. The common methods are implemented in this abstract method.
    """
    def __init__(self):
        self._logger        = None
        self._configure_logger(logger_config_path=LOGGER_CONFIG_PATH, save_root_dir=str(CURRENTDIR))

        self._smtp_config   = SmtpParams(**yaml.safe_load(open(MAIL_SENDER_CONFIG_PATH, "r")))
        self._strage_params = StrageParams(**yaml.safe_load(open(CLOUD_STRAGE_CONFIG_PATH, "r")))
        self._get_mail_config(config=self._smtp_config)

        if os.path.exists(str(MAIL_RECORD_PATH)):
            self._last_mail_record = yaml.safe_load(open(MAIL_RECORD_PATH, "r"))
        else:
            self._last_mail_record = {"log_path": False, "line_no": 0}

        self._s3_time_str   = self._strage_params.FILE_TIME_STR # "%Y-%m-%d %H:%M:%S"

    def main(self):
        """The main method of this class.
        This methods is repeatedly looping with interval of 180s if there is no updates in log file. 
        If there is updates in log files, mail sending process is executed.
        """
        self._logger.info("[Checkpont] enter main")
        while(True):
            self._logger.info("[Checkpont] start checking log update")

            latest_dir_path = self._get_latest_dir()
            self._logger.debug('[Variables]  latest_dir_path: %s' %latest_dir_path)

            log_path = self._get_latest_log_path(job_dir=latest_dir_path)
            self._logger.debug('[Variables]  log_path: %s' %log_path)

            mail_status, msg, line_no = self._get_mail_status(log_path=log_path)
            self._logger.debug('[Variables]  mail_status: %s' %mail_status)
            self._logger.debug('[Variables]  msg: %s' %msg)
            self._logger.debug('[Variables]  line_no: %s' %line_no)

            self._logger.info("[Checkpoint] done checking log_update")
            self._logger.debug('[BranchPoint]  self._check_status_is_not_sent(log_path=log_path, line_no=line_no, last_mail_config=self._last_mail_record): %s' %self._check_status_is_not_sent(log_path=log_path, line_no=line_no, last_mail_config=self._last_mail_record))
            if self._check_status_is_not_sent(log_path=log_path, line_no=line_no, last_mail_config=self._last_mail_record):
                _ = self._send(
                    log_path=log_path,
                    job_dir=latest_dir_path,
                    status=mail_status,
                    msg=msg,
                    config=self._smtp_config
                )
                self._last_mail_record["log_path"] = str(log_path)
                self._last_mail_record["line_no"]  = line_no
                self._logger.debug('[Variables]  self._last_mail_record: %s' %self._last_mail_record)
                self._save_mail_status(config=self._last_mail_record, config_path=str(MAIL_RECORD_PATH))
            else:
                time.sleep(60*3)

    def monitor_s3(self):
        self._logger.info("[Checkpont] enter monitor_s3")
        latest_dir_path = self._get_latest_dir()
        self._logger.debug("[Variables] latest_dir_path: %s" %latest_dir_path)

        log_path = self._get_latest_log_path(job_dir=latest_dir_path)
        self._logger.debug("[Variables] log_path: %s" %log_path)

        mail_status, msg, line_no = self._get_mail_status(log_path=log_path)
        ret = self._check_status_is_not_sent(log_path=log_path, line_no=line_no, last_mail_config=self._last_mail_record)
        self._logger.debug("[Variables] ret: %s" %ret)
        self._logger.debug("[Variables] mail_status: %s, msg: %s, line_no: %s, latest_dir_path: %s, log_path: %s" %(mail_status, msg, line_no, latest_dir_path, log_path))
        self._logger.info("[Checkpont] enter monitor_s3")

    def send_mail(self, log_path: str, latest_dir_path: str, mail_status: str, msg: str, line_no: int):
        _ = self._send(
            log_path=log_path,
            job_dir=latest_dir_path,
            status=mail_status,
            msg=msg,
            config=self._smtp_config
        )
        self._last_mail_record["log_path"] = str(log_path)
        self._last_mail_record["line_no"]  = line_no
        self._logger.debug('[Variables]  self._last_mail_record: %s' %self._last_mail_record)
        self._save_mail_status(config=self._last_mail_record, config_path=str(MAIL_RECORD_PATH))

    def _configure_logger(self, logger_config_path: str, save_root_dir: str)-> logging.Logger:
        if not os.path.exists(logger_config_path):
            raise ValueError("No such file at the path: %s" %logger_config_path)
        self._logger = configure_logger(log_config_path=logger_config_path, output_dir=str(Path(save_root_dir) / "log"))
        self._set_logger(logger=self._logger)
        return self._logger

    def _get_img_lst4done(self, job_dir: str)-> list:
        self._logger.debug("[Checkpoint] enter _get_img_lst4done")
        self._logger.debug("[Variables] job_dir: %s" %job_dir)

        tray_names = self._search(search_dir=job_dir)
        self._logger.debug("[Variables] tray_names: %s" %tray_names)

        fles = []

        for tray_name in tray_names:
            self._logger.debug("[Variables] fles: %s" %fles)
            try:
                fles.extend(self._search(search_dir=str(Path(job_dir) / tray_name / "tray_img"), is_file=True))
            except Exception as e:
                self._logger.error("[Error] error_msg: %s" %e)
            self._logger.debug("[Variables] fles: %s" %fles)
        try:
            self._logger.debug("[Variables] fles: %s" %fles)
            fles.extend(self._search(search_dir=str(Path(job_dir) / tray_names[-1] / "visualize_data"), is_file=True)[-2:])
            self._logger.debug("[Variables] fles: %s" %fles)
        except Exception as e:
            self._logger.error("[Error] error_msg: %s" %e)
        self._logger.debug("[Variables] fles: %s" %fles)

        fles = self._copy2local(fles=fles, local_root_dir=str(CURRENTDIR))
        self._logger.debug("[Variables] fles: %s" %fles)

        self._logger.debug("[Checkpoint] exit _get_img_lst4done")
        return fles

    def _get_latest_dir(self)-> str:
        self._logger.debug("[Checkpoint] enter _get_latest_dir")

        ui_modes = self._search(search_dir=self._strage_params.ROOT_DIR)
        self._logger.debug("[Variables] ui_modes: %s" %ui_modes)

        ui_modes = ["run_results/"]

        latest_dir_path = None
        self._logger.debug("[Variables] latest_dir_path: %s" %latest_dir_path)

        for ui_mode in ui_modes:
            dir_lst = self._search(search_dir=str(self._strage_params.ROOT_DIR + ui_mode))
            self._logger.debug("[Variables] dir_lst: %s" %dir_lst)

            self._logger.debug('[BranchPoint]  (latest_dir_path is None): %s' %(latest_dir_path is None))

            self._logger.debug('[BranchPoint]  (latest_dir_path is None): %s' %(latest_dir_path is None))
            if latest_dir_path is None:
                latest_dir_path = self._strage_params.ROOT_DIR + ui_mode + dir_lst[-1]
                self._logger.debug("[Variables] latest_dir_path: %s" %latest_dir_path)
            elif (self._get_modified_time(latest_dir_path, is_file=False) - self._get_modified_time(dir_lst[-1], is_file=False)).seconds < 0:
                latest_dir_path = self._strage_params.ROOT_DIR + ui_mode + dir_lst[-1]
                self._logger.debug("[Variables] latest_dir_path: %s" %latest_dir_path)

        self._logger.debug("[Variables] latest_dir_path: %s" %latest_dir_path)
        self._logger.debug("[Checkpoint] exit _get_latest_dir")
        return latest_dir_path

    def _get_latest_log_path(self, job_dir: str)-> str:
        self._logger.debug("[Checkpoint] enter _get_latest_log_path")
        self._logger.debug("[Variables] job_dir: %s" %job_dir)

        tray_dirs = self._search(search_dir=f"{job_dir}")
        self._logger.info("[Variables] tray_dirs: %s" %tray_dirs)

        log_files = self._search(search_dir=f"{job_dir}{tray_dirs[-1]}log/", is_file=True)
        self._logger.debug("[Variables] log_files: %s" %log_files)

        log_path = [f'{job_dir}{tray_dirs[-1]}log/{ele}' for ele in log_files if (("logger_" in ele) and ("process" in ele))][0]
        self._logger.debug("[Variables] log_path: %s" %log_path)

        log_path = self._copy2local(fles=[log_path], local_root_dir=str(CURRENTDIR / "tmp"))[0] 
        self._logger.debug("[Variables] log_path: %s" %log_path)

        self._logger.debug("[Checkpoint] exit _get_latest_log_path")
        return log_path

    def _get_modified_time(self, path: str, is_file: bool=False)-> datetime:
        """This method returns the modified time of the target file or directory.
        Unlike local strage, s3 container actually doesnot has directory or folder.
        Therefore, in this methods, only job result directories and tray result directories can get thier modified time.

        Args:
            path (str): The absolute path of the file or the directory.
            is_file (bool, optional): The booling flag whether input path is file or directory, as getting modified time procedure is different for those two types un s3 strages. Defaults to False.

        Returns:
            datetime: The modified time in datetime format as it is easy to calculate.
        """
        self._logger.debug("[Checkpoint] enter _get_modified_time")

        self._logger.debug("[Variables] path: %s" %path)
        self._logger.debug("[Variables] is_file: %s" %is_file)

        if is_file:
            ret = self._get_fle_modified_time(fle_path=path)
        else:
            ret = self._get_dir_modified_time(dire=path)

        self._logger.debug("[Variables] ret: %s" %ret)
        self._logger.debug("[Checkpoint] exit _get_modified_time")
        return ret

    def _search(self, search_dir: str, is_file: bool=False)-> list:
        self._logger.debug("[Checkpoint] enter _search")
        self._logger.debug("[Variables] search_dir: %s" %search_dir)
        self._logger.debug("[Variables] is_file: %s" %is_file)

        ret = self._search_cloud(search_dir=search_dir, is_file=is_file)
        self._logger.debug("[Variables] ret: %s" %ret)

        self._logger.debug("[Checkpoint] exit _search")
        return ret

    def _send(self, log_path: str, job_dir: str, status: str, msg: str, config: dict) -> bool:
        """This method contains the main process of mail sending

        Args:
            log_path (str): The absolute path of the log file.
            job_dir (str): The absolute path of the results and log files saved. In this class, this sould be in s3 container.
            status (str): The current mail status.
            msg (str): The message corresponded to the current mail status. 
            config (dict): The config objects of the smtp process, with smtp server ip address and port number, mail addresses of sender and reciever, and etc...

        Returns:
            bool: Returns True if mail successfully sent, else returns False.
        """
        self._logger.debug("[Checkpoint] enter _send")

        self._logger.debug("[Variables] log_path: %s" %log_path)
        self._logger.debug("[Variables] job_dir: %s" %job_dir)
        self._logger.debug("[Variables] status: %s" %status)
        self._logger.debug("[Variables] msg: %s" %msg)
        self._logger.debug("[Variables] config: %s" %config)

        attachments = []
        # self._get_mail_config(config=config)

        ui_mode = self._get_ui_mode(job_dir=job_dir)
        self._logger.debug("[Variables] ui_mode: %s" %ui_mode)

        attachment_files = self._fetch_attachment_lst(job_dir=job_dir, log_path=log_path, status=status)
        self._logger.debug("[Variables] attachment_files: %s" %attachment_files)

        for fle in attachment_files:
            attachments = self._get_attachment(fle_path=fle, attachments=attachments)
        self._logger.debug("[Variables] attachments: %s" %attachments)

        str_subject, str_msg = self._get_mailtext(status=status, ui_mode=ui_mode, msg=msg)
        self._logger.debug("[Variables] str_subject: %s" %str_subject)
        self._logger.debug("[Variables] str_msg: %s" %str_msg)

        for idx in range(len(self._from_addrs)):
            mailpart = self._create_mailpart(
                subject=str_subject,
                from_addrs=self._from_addrs[idx],
                to_addrs=self._to_addrs[idx],
                msg=str_msg,
                attachments=attachments
            )
            self._logger.debug("[Variables] mailpart: %s" %mailpart)

            ret = self._send_smtpobj(
                smtp_server=self._smtp_server[idx],
                smtp_port=self._smtp_port[idx],
                from_addrs=self._from_addrs[idx],
                to_addrs=self._to_addrs[idx],
                passwd=self._maillist["password"][idx],
                need_auth=self._need_auth[idx],
                mailpart=mailpart
            )
            self._logger.debug("[Variables] ret: %s" %ret)

        self._logger.debug("[Variables] ret: %s" %ret)
        self._logger.debug("[Checkpoint] exit _send")
        return ret

    def _copy(self, from_path: str, to_path: str)-> str:
        """This method copies files from or to s3 container.

        Args:
            from_path (str): The absolute path of the copied file path.
            to_path (str): The absolute path of the copying file path. If the file is copied to s3 container, s3 container path have to be finished with "/".

        Returns:
            str: Returns the copying file absolute path.
        """
        self._logger.debug("[Checkpoint] enter _copy")

        self._logger.debug("[Variables] from_path: %s" %from_path)
        self._logger.debug("[Variables] to_path: %s" %to_path)

        ret = subprocess.run(["aws", "s3", "cp", from_path, to_path], encoding="utf-8", stdout=subprocess.PIPE).stdout

        self._logger.debug("[Variables] ret: %s" %ret)
        self._logger.debug("[Checkpoint] exit _copy")
        return ret

    def _copy2local(self, fles: list, local_root_dir: str)-> list:
        """This method copies the files in s3 container to the local directories.

        Args:
            fles (list): The list of files to be copied to local.
            local_root_dir (str): The root directory path of the local environment in absolute format.

        Returns:
            list: Returns the list of the locally saved files absolute path.
        """
        self._logger.debug("[Checkpoint] enter _copy2local")

        self._logger.debug("[Variables] fles: %s" %fles)
        self._logger.debug("[Variables] local_root_dir: %s" %local_root_dir)

        ret = []
        self._logger.debug("[Variables] ret: %s" %ret)

        for fle in fles:
            self._logger.debug("[Variables] fle: %s" %fle)
            # relative_path = fle.split(self._strage_params.ROOT_DIR+"/", 1)[-1]  # s3_root_dir / job_dir / tray_dir / log / fle_name
            _, job_dir, tray_dir, log_dir, fname = fle.rsplit("/", 4)  
            relative_path = str(Path(job_dir) / tray_dir / log_dir / fname)
            self._logger.debug("[Variables] relative_path: %s" %relative_path)

            save_path = Path(local_root_dir).resolve() / relative_path
            self._logger.debug("[Variables] save_path: %s" %save_path)

            _ = self._copy(from_path=fle, to_path=str(save_path))
            ret.append(str(save_path))
            self._logger.debug("[Variables] ret: %s" %ret)

        self._logger.debug("[Variables] ret: %s" %ret)
        self._logger.debug("[Checkpoint] exit _copy2local")
        return ret

    def _fetch_attachment_lst(self, job_dir: str, log_path: str, status: str)-> list:
        self._logger.debug("[Checkpoint] enter _fetch_attachment_lst")

        self._logger.debug("[Variables] job_dir: %s" %job_dir)
        self._logger.debug("[Variables] log_path: %s" %log_path)
        self._logger.debug("[Variables] status: %s" %status)

        attachment_files = []
        self._logger.debug("[Variables] attachment_files: %s" %attachment_files)

        self._logger.debug('[BranchPoint]  (status is "Start"): %s' %(status is "Start"))
        self._logger.debug('[BranchPoint]  (status is "Error"): %s' %(status is "Error"))
        self._logger.debug('[BranchPoint]  (status is "Done"): %s' %(status is "Done"))
        if status is "Start":
            pass
        elif status is "Error":
            attachment_files.append(log_path)
        elif status is "Done":
            attachment_files.extend(self._get_img_lst4done(job_dir=job_dir))

        self._logger.debug("[Variables] attachment_files: %s" %attachment_files)
        self._logger.debug("[Checkpoint] exit _fetch_attachment_lst")
        return attachment_files

    def _get_dir_modified_time(self, dire: str)-> datetime:
        """This method gets the modified time of the directory in s3 strage.
        As the s3 strage actually doesnot have directory, we assume the directory is modified when job result directory was created.

        Args:
            dire (str): The absolute path of the directory which modified time is needed.

        Returns:
            datetime: _description_
        """
        self._logger.debug("[Checkpoint] enter _get_dir_modified_time")

        self._logger.debug("[Variables] dire: %s" %dire)
        self._logger.debug("[Variables] dire.rsplit('/', 2)[-2]: %s" %dire.rsplit("/", 2)[-2])

        ret = datetime.strptime(dire.rsplit("/", 2)[-2], self._strage_params.TIME_FORMAT)
        self._logger.debug("[Variables] ret: %s" %ret)

        self._logger.debug("[Checkpoint] exit _get_dir_modified_time")
        return ret

    def _get_fle_modified_time(self, fle_path: str)-> datetime:
        self._logger.debug("[Checkpoint] enter _get_fle_modified_time")

        self._logger.debug("[Variables] fle_path: %s" %fle_path)

        fle_prop = self._search(fle_path, is_file=True)
        self._logger.debug("[Variables] fle_prop: %s" %fle_prop)

        date, time, _ = fle_prop[0].split(" ", 2)
        self._logger.debug("[Variables] date: %s" %date)
        self._logger.debug("[Variables] time: %s" %time)

        ret = datetime.strptime(f"{date} {time}", self._s3_time_str)

        self._logger.debug("[Variables] ret: %s" %ret)
        self._logger.debug("[Checkpoint] exit _get_fle_modified_time")
        return ret

    def _search_cloud(self, search_dir: str, is_file: bool=False)-> list:
        self._logger.debug("[Checkpoint] enter _search_cloud")

        self._logger.debug("[Variables] search_dir: %s" %search_dir)
        self._logger.debug("[Variables] is_file: %s" %is_file)

        output = subprocess.run(["aws", "s3", "ls", f"{search_dir}"], encoding="utf-8", stdout=subprocess.PIPE).stdout.rsplit("\n")
        self._logger.debug("[Variables] output: %s" %output)

        self._logger.debug('[BranchPoint]  is_file: %s' %is_file)
        if is_file:
            ret = sorted([ele.rsplit(" ", 1)[-1] for ele in output if (("PRE " not in ele) and (" " in ele))])
        else:
            ret = sorted([ele.rsplit("PRE ", 1)[-1] for ele in output if "PRE " in ele])

        self._logger.debug("[Variables] ret: %s" %ret)
        self._logger.debug("[Checkpoint] exit _search_cloud")
        return ret


class MailSender4local(MailSender):
    def __init__(self):
        self._smtp_config   = SmtpParams(**yaml.safe_load(open(MAIL_SENDER_CONFIG_PATH, "r")))
        self._strage_params = StrageParams(**yaml.safe_load(open(LOCAL_STRAGE_CONFIG_PATH, "r")))

    def _configure_logger(self, logger_config_path: str, save_root_dir: str)-> logging.Logger:
        pass

    def _fetch_attachment_lst(self, job_dir: str, log_path: str, status: str)-> list:
        pass

    def _get_img_lst4done(self, job_dir: str)-> list:
        pass

    def _get_latest_dir(self)-> str:
        ui_modes = self._search_local(search_dir=self._strage_params.ROOT_DIR)
        latest_dir_path = None
        for ui_mode in ui_modes:
            dir_lst = self._search_local(search_dir=str(self._strage_params.ROOT_DIR) / ui_mode)
            if latest_dir_path is None:
                latest_dir_path = dir_lst[-1]
            elif (self._get_modified_time(latest_dir_path) - self._get_modified_time(dir_lst[-1])) < 0:
                latest_dir_path = dir_lst[-1]
        return latest_dir_path

    def _get_latest_log_path(self, job_dir: str)-> str:
        pass

    def _get_modified_time(self, fle: str)-> datetime:
        return Path(fle).stat().st_mtime.fromtimestamp(self._strage_params.TIME_FORMAT)

    def _search(self, search_dir: str, is_file: bool=False)-> list:
        return self._search_local(search_dir=search_dir)

    def _search_local(self, search_dir: str)-> list:
        elements = sorted(glob(str(search_dir) / "*"))
        ret = sorted([ret.rsplit("/", 1)[-1] for ret in elements])
        return ret


if __name__ == "__main__":
    mail_sender = MailSender4ec2()

    # # monitoring test
    # mail_sender.monitor_s3()

    # mailing test
    log_path = "/home/saito/sandbox/ec2_mail_sender/tmp/2022-07-13_17:36:44/2022-07-13_17:36:44/log/logger_kitting_process.log"
    latest_dir_path = "s3://robot-arm-dataset1/SHIBAHARA_results/test_uploader/run_results/2022-07-13_17:36:44/"
    mail_status = "error"
    msg = "test"
    line_no = 75
    mail_sender.send_mail(log_path=log_path, latest_dir_path=latest_dir_path, mail_status=mail_status, msg=msg, line_no=line_no)
