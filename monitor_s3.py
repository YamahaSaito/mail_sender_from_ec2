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

    def _check_status(self, target_root_dir: str)-> Tuple[str, list]:
        ret_lst = self._search(target_root_dir) # returns job_result_dir
        ret_lst = self._search(ret_lst[-1])     # return tray dirs in latest job
        ret_lst = self._search(ret_lst[-1] + "/log")
        for ele in ret_lst:
            if "_process" in ele:
                log_exists = True
                target_path = ele
        if log_exists:
            fle_path = self._fetch_fle(target_path=target_path, save_dir=str(CURRENTDIR/"tmp"))
