import os
import sys
import subprocess

from pathlib import Path
from glob import glob
from dataclasses import asdict, dataclass
from datetime import datetime

import yaml

CURRENTDIR = Path(__file__).resolve().parent
S3_PARAM_PATH = str(CURRENTDIR / "config" / "s3_uploader" / "s3_config.yaml")


@dataclass(frozen=True)
class S3Params:
    STRAGE_ROOT_DIR        : str
    LAST_UPLOADED_TIMESTAMP: str

    def _post_init_(self):

        user_dict = asdict(self)
        for user_arg_name, user_arg_expected_type in self._annotations_.items():

            if not isinstance(user_dict[user_arg_name], user_arg_expected_type):
                raise TypeError("type mismatch: the type of content {%s} shuold match with the registered type {%s}" %(user_dict[user_arg_name], user_arg_expected_type))


class S3Uploader:
    """This class is aimed to upload local files quickly to s3 container.
    As 'aws s3 sync' commands is very slow when the target directory has a lot of files.
    Therefore this class uploads the local data instead of 'aws s3 sync' commands by following 5steps.
    1. Get s3 root directory path ahd latest uploaded timestamp from externally recorded config file, 'S3_PARAM_PATH'
    2. Get local files list and removed the files in too old directory compared to latest uploaded timestamp.(valid_file_lst)
    3. Get the files list which is either newly created or modified after last uplaods, by comparing file modified time and last uploaded timestamp one by one.
    4. Upload target files one by one with 'aws s3 cp' commands.
    """
    def __init__(self, local_root_dir: str):
        self._params         = S3Params()
        self._time_format    = "%Y-%m-%d_%H:%M:%S"
        self._local_root_dir = Path(local_root_dir).resolve()
        self._last_timestamp = datetime.strptime(self._params.LAST_UPLOADED_TIMESTAMP, self._time_format)

    def main(self):
        """Main method of S3Uploader.
        Basically, upload the files which is newer than last upload time in given local directly.
        """
        self._upload2s3(fle_lst=self._get_modified_fle_lst())
        self._save_config()

    def _check_is_modified_file(self, fle: str, basetime: datetime)-> bool:
        """This method checks whether the target file is modified or created after last uploading.

        Args:
            fle (str): The file path needs to be checked. Accepts both absolute and relative path, but basically absolute path is preferred.
            basetime (datetime): The basic time to be compared.Basically, this is the last uploaded time saved in config file.

        Returns:
            bool: Return True if the target file is either modified or created after last uploading.
        """
        fle_stat = Path(fle).stat()
        if (fle_stat.st_mtime - fle_stat.st_atime) > 0:
            dt_data = datetime.fromtimestamp(fle_stat.st_mtime)
        else:
            dt_data = datetime.fromtimestamp(fle_stat.st_atime)
        return True if (dt_data - basetime) > 0 else False

    def _get_local_fle_lst(self)-> list:
        """This method is to get local file list under given local directory.
        Before returns file list, it removes too old files and directories to prevent time wasting.

        Returns:
            list: Rerturn the file list under the given local directory and stisfied 'new file' condition.
        """
        fles = sorted(glob(str(self._local_root_dir / "**" / "*"), recursive=True))
        valid_fles = []
        for ele in fles:
            tray_created_time = datetime.strptime(ele.split(str(self._local_root_dir), 1)[-1].split("/", 4)[3], self._time_format)
            if (tray_created_time - self._last_timestamp).days < 1:
                valid_fles.append(ele)
        return valid_fles

    def _get_modified_fle_lst(self)-> list:
        """This method returns the satisfatory "new" file list under the given local directory.

        Returns:
            list: The list of the satisfactory "new" file list under the given local directory.
        """
        valid_lst = self._get_local_fle_lst()
        target_lst = [ele for ele in valid_lst if self._check_is_modified_file(fle=ele, basetime=self._last_timestamp)]
        return target_lst

    def _save_config(self)-> bool:
        """This method is to save the configs for the next upload.

        Returns:
            bool: Returns True if the configs are saved successfully.
        """
        config = {
            "STRAGE_ROOT_DIR": str(self._params.STRAGE_ROOT_DIR),
            "LAST_UPLOADED_TIMESTAMP": datetime.datetime.now.strftime(self._time_format)
        }
        with open(S3_PARAM_PATH, "w") as f:
            yaml.safe_dump(config, f)
        return True

    def _upload2s3(self, fle_lst: list)-> bool:
        """This method uploads the given files to the S3 container given at the config file file by file/

        Args:
            fle_lst (list): The list of the files to be uploaded. Accepts both absolute and relative path.

        Returns:
            bool: Returns True if all uploading successed.
        """
        for fle in fle_lst:
            part_save_path = fle.split(str(self._local_root_dir), 1)[-1]
            save_path = Path(self._params.STRAGE_ROOT_DIR) / part_save_path
            _= subprocess.run(["aws", "s3", "cp", fle, f"{str(save_path.parent)}/"], encoding="utf-8", stdout=subprocess.PIPE)
        return True
