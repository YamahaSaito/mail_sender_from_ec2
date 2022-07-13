import os
import logging.config
from pathlib import Path
from datetime import datetime

import yaml


TIME_STR_FORMAT = "%Y-%m-%d_%H-%M-%S"


def configure_logger(log_config_path:str, output_dir:str):
    """loggerを設定する

    Args:
        log_config_path (str): ログ設定ファイル(yaml)
        output_dir (str): ログ出力先ディレクトリ
                          ログ出力先ディレクトリ内に各logが保存される

    Returns:
        : logger
    """
    output_dir = Path(output_dir).resolve()

    os.makedirs(str(output_dir), mode=0o777, exist_ok=True)

    yaml_loader = yaml.safe_load(open(log_config_path).read())
    time_str    = datetime.now().strftime(TIME_STR_FORMAT)

    for name in yaml_loader["handlers"]:
        if("fh" in name):
            # yaml_loader["handlers"][name]["filename"] = str(output_dir / f'{time_str}_{yaml_loader["handlers"][name]["filename"]}')
            yaml_loader["handlers"][name]["filename"] = str(output_dir / f'{yaml_loader["handlers"][name]["filename"]}')

    logging.config.dictConfig(yaml_loader)

    return logging.getLogger()

def close_logger(logger):
    """loggerから特定のハンドルを削除する

    Args:
        arg_logger (logging.Logger): ハンドルを削除したいロガー(logging.Logger)
    """
    handlers = logger.handlers

    logger.info('before removing. %d handlers: %s' %(len(handlers), 
                                                     str(handlers)))

    # 既存の全てのloggerを削除する
    # for文で回すと全てをうまく消せない
    #for handler in handlers:
    while len(handlers) > 0:
        handler = logger.handlers[0]
        logger.info('removing handler %s' %str(handler))
        # loggerから特定のハンドルを削除する
        logger.removeHandler(handler)
        handler.close()

    # このlogは出力されない
    logger.info('after removing: %d handlers: %s' %(len(handlers),
                                                    str(handlers)))
if __name__ == "__main__":
    logger = configure_logger(file, "./logfile")
    close_logger(logger)