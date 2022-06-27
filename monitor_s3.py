from dataclasses import dataclass, asdict
from glob import glob
from pathlib import Path
import os
import sys
import shutil
import subprocess
from typing import Tuple


import yaml


CURRENTDIR = Path(__file__).resolve().parent
CONFIG_PATH = str(CURRENTDIR.parent / "config" / "storage_monitor_configs.yaml")


@dataclass(frozen=True)
class StorageMonitorParams():
    """Parameter class of Storage Monitor class.
    Loading parameters from yaml file

    Raises:
        TypeError: raises if the type of the parameter does not match with the registered type
    """
    STORAGE_ROOT_DIR: str
    RESULT_TYPE_LIST: list

    def _post_init_(self):

        user_dict = asdict(self)
        for user_arg_name, user_arg_expected_type in self._annotations_.items():

            if not isinstance(user_dict[user_arg_name], user_arg_expected_type):
                raise TypeError("type mismatch: the type of content {%s} shuold match with the registered type {%s}" %(user_dict[user_arg_name], user_arg_expected_type))


class StrageMonitor:
    def __init__(self):
        if not os.path.exists(CONFIG_PATH):
            raise ValueError("file does not exists : %s" %CONFIG_PATH)
        self._params = StorageMonitorParams(**yaml.safe_load(open(CONFIG_PATH, "r")))
        self._mail_status_list = ["Start", "Error", "Done"]

    def _search(self, target_dir_path: str)-> str:
        if "s3://" in target_dir_path:
            ret_lst = self._search_on_s3(target_dir_path)
        else:
            ret_lst = self._search_on_local(target_dir_path)
        return ret_lst

    def _search_on_s3(self, target_dir_path: str)-> list:
        ret_lst = subprocess.run(["aws", "s3", "ls", target_dir_path+"/"], encoding="utf-8", stdout=subprocess.PIPE).stdout.rsplit("\n")
        ret_lst = [target_dir_path + "/" + ele.rsplit("PRE ", 1)[-1] for ele in ret_lst if "PRE " in ele]
        return ret_lst

    def _search_on_local(self, target_dir_path: str)-> list:
        ret_lst = sorted(glob(target_dir_path + "/*"))
        return ret_lst

    def _fetch_fle(self, target_path: str, save_dir_path: str = str(CURRENTDIR / "tmp"))-> str:
        if "s3://" in target_path:
            ret = self._fetch_fle_from_s3(target_path, save_dir_path)
        else:
            ret = self._fetch_fle_from_local(target_path, save_dir_path)
        return ret

    def _fetch_fle_from_s3(self, target_path: str, save_dir_path: str)-> str:
        _ = subprocess.run(["aws", "s3", "cp", target_path, save_dir_path + "/"], encoding="utf-8", stdout=subprocess.PIPE)
        return save_dir_path + "/" + target_path.rsplit("/", 1)[-1]

    def _fetch_fle_from_local(self, target_path: str, save_dir_path: str)-> str:
        save_path = save_dir_path + "/" + target_path.rsplit("/", 1)[-1]
        if not os.path.exists(save_dir_path):
            os.makedirs(save_dir_path, exist_ok=True)
        shutil.copy(target_path, save_path)
        return save_path

    def main(self, target_root_dir: str)-> Tuple[str, str]:
        ret_lst = self._search(target_root_dir) # returns job_result_dir
        ret_lst = self._search(ret_lst[-1])     # return tray dirs in latest job
        ret_lst = self._search(ret_lst[-1] + "/log")
        for ele in ret_lst:
            if "_process" in ele:
                log_exists = True
                target_path = ele
        if not log_exists:
            fle_path = "none"
            status   = "no fle available"
        else:
            fle_path = self._fetch_fle(target_path=target_path, save_dir=str(CURRENTDIR/"tmp"))
            status   = self._check_status(fle_path=fle_path)
        return status, fle_path

    def _check_status(self, fle_path: str)-> str:
        with open(fle_path, "r") as f:
            data = f.read().rsplit("\n")

        status = "Start"

        for ele in data:
            if "Mail_Status::" in ele:
                status = ele.rsplit("Mail_Status", 1)[-1]
        return status

    def _fetch_attachment_fles(self, fle_path: str, status: str)-> list:
        fles = [fle_path]
        if status == "done":
            root_dir, _, _ = fle_path.rsplit("/", 2)
            if os.path.exists(str(Path(root_dir) / "visualize_data" / "pickrate.png")):
                fles.append(str(Path(root_dir) / "visualize_data" / "pickrate.png"))
            if os.path.exists(str(Path(root_dir) / "visualize_data" / "picktime.png")):
                fles.append(str(Path(root_dir) / "visualize_data" / "picktime.png"))
            tray_imgs = sorted(glob(str(Path(root_dir).parent / "**" / "tray_img" / "*.jpg")))
            if len(tray_imgs) > 1:
                fles.extend(tray_imgs)
            elif len(tray_imgs) == 1:
                fles.append(tray_imgs)
        return fles

    def _get_mail_state(self, status: str)-> str:
        if "Start":
            ret = "start"
        elif "Error":
            ret = "error"
        elif "Done":
            ret = "done"
        else:
            raise ValueError("Invalid state: %s, state must be either %s" %(status, self._mail_status_list))
        return ret

    def _get_ui_mode_from_fle(self, log_fle_path: str)-> str:
        _, ui_type, _, _, _, _ = log_fle_path.rsplit("/", 5)
        if "run" in ui_type:
            ret = "run_ui"
        elif "train" in ui_type:
            ret = "train_ui"
        elif "pickuptest" in ui_type:
            ret = "pickuptest_ui"
        else:
            raise ValueError("Invalid UI_type: %s" %ui_type)
        return ret

    def monitor_mail_status(self, target_root_dir: str):
        from send_mail import SendSmtp
        send_smtp = SendSmtp()

        monitor_process = False

        while (monitor_process):
            status, fle_path = self.main(target_root_dir)
            if status in self._mail_status_list:
                fles = self._fetch_attachment_fles(fle_path=fle_path, status=status)
                ret = send_smtp.send_mail(attachment_fles=fles, state=self._get_mail_state(status), ui_mode=self._get_ui_mode_from_fle(fles[0]))
                if ret:
                    monitor_process = True
                    break
