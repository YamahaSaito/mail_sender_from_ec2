from error_code import error_code_map


class RobotException():
    """
    ロボットに関するエラーを定義するクラスです。
    """
    class Code1(Exception):
        """エラーコード１のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self, msg=""):
            self._msg = error_code_map["001.001"] + ":\n\r" +msg

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code2(Exception):
        """エラーコード２のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["001.002"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code3(Exception):
        """エラーコード３のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["001.003"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code4(Exception):
        """エラーコード４のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["001.004"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code5(Exception):
        """エラーコード５のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["001.005"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code6(Exception):
        """エラーコード６のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["001.006"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code7(Exception):
        """エラーコード7のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["001.007"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code8(Exception):
        """エラーコード8のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["001.008"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class TimeOut(Exception):
        """タイムアウトした場合に発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = "Timeout Occurred while waiting for response from Robot."

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class ValueError(Exception):
        def __init__(self, msg=""):
            """値が妥当ではない場合、こちらのエラーを使用します。

            Args:
                msg (str): エラーメッセージ
            """
            self._msg = msg

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Else(Exception):
        def __init__(self, msg=""):
            """本クラスの外部クラス内にないエラーを発生させたい場合はこちらを利用します。

            Args:
                msg ([str]): 表示させたいエラーメッセージ
            """
            self._msg = msg

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)


class DepthCameraException():
    """
    深度カメラに関するエラーを定義するクラスです。
    """
    class Code1(Exception):
        """エラーコード１のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["002.001"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code2(Exception):
        """エラーコード２のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["002.002"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code3(Exception):
        """エラーコード３のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["002.003"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code4(Exception):
        """エラーコード４のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["002.004"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code5(Exception):
        """エラーコード５のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["002.005"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Else(Exception):
        """本クラスの外部クラス内にないエラーを発生させたい場合はこちらを利用します。

        Args:
            msg ([str]): 表示させたいエラーメッセージ
        """
        def __init__(self, msg=""):
            self._msg = msg

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)


class USBCameraException():
    """
    USBカメラに関するエラーを定義するクラスです。
    """
    class Code1(Exception):
        """エラーコード１のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["003.001"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Else(Exception):
        """本クラスの外部クラス内にないエラーを発生させたい場合はこちらを利用します。

        Args:
            msg ([str]): 表示させたいエラーメッセージ
        """
        def __init__(self, msg=""):
            self._msg = msg

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)


class LoadersException():
    """
    ローダ・アンローダに関するエラーを定義するクラスです。
    """
    class Code1(Exception):
        """エラーコード１のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["004.001"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code2(Exception):
        """エラーコード２のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["004.002"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code3(Exception):
        """エラーコード３のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["004.003"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code4(Exception):
        """エラーコード４のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["004.004"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code5(Exception):
        """エラーコード５のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["004.005"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code6(Exception):
        """エラーコード６のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["004.006"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code7(Exception):
        """エラーコード７のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["004.007"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code8(Exception):
        """エラーコード８のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["004.008"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code9(Exception):
        """エラーコード９のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["004.009"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code10(Exception):
        """エラーコード１０のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["004.010"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code11(Exception):
        """エラーコード１１のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["004.011"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Else(Exception):
        """本クラスの外部クラス内にないエラーを発生させたい場合はこちらを利用します。

        Args:
            msg ([str]): 表示させたいエラーメッセージ
        """
        def __init__(self, msg=""):
            self._msg = msg

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)


class TrayBinException():
    """
    トレイまたはビンに関するエラーを定義するクラスです。
    """

    class Code1(Exception):
        """エラーコード１のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["005.001"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code2(Exception):
        """エラーコード２のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["005.002"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code3(Exception):
        """エラーコード３のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["005.003"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code4(Exception):
        """エラーコード４のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["005.004"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code5(Exception):
        """エラーコード５のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["005.004"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Else(Exception):
        """本クラスの外部クラス内にないエラーを発生させたい場合はこちらを利用します。

        Args:
            msg ([str]): 表示させたいエラーメッセージ
        """
        def __init__(self, msg=""):
            self._msg = msg

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)


class MassScaleException():
    """
    質量計に関するエラーを定義するクラスです。
    """

    class Code1(Exception):
        """エラーコード１のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["006.001"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code2(Exception):
        """エラーコード２のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["006.002"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code3(Exception):
        """エラーコード３のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["006.003"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Else(Exception):
        """本クラスの外部クラス内にないエラーを発生させたい場合はこちらを利用します。

        Args:
            msg ([str]): 表示させたいエラーメッセージ
        """
        def __init__(self, msg=""):
            self._msg = msg

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)


class QRException():
    """
    QRコードに関するエラーを定義するクラスです。
    """

    class Code1(Exception):
        """エラーコード１のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["007.001"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code2(Exception):
        """エラーコード２のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["007.002"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code3(Exception):
        """エラーコード３のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["007.003"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Else(Exception):
        """本クラスの外部クラス内にないエラーを発生させたい場合はこちらを利用します。

        Args:
            msg ([str]): 表示させたいエラーメッセージ
        """
        def __init__(self, msg):
            self._msg = msg

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

class DeliverablesException():
    """
    成果物(ファイル、グラフ)・メールに関するエラーを定義するクラスです。
    """

    class Code1(Exception):
        """エラーコード１のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["008.001"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code2(Exception):
        """エラーコード２のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["008.002"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Code3(Exception):
        """エラーコード３のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["008.003"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Else(Exception):
        """本クラスの外部クラス内にないエラーを発生させたい場合はこちらを利用します。

        Args:
            msg ([str]): 表示させたいエラーメッセージ
        """
        def __init__(self, msg):
            self._msg = msg

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

class AIException():
    """
    AIに関するエラーを定義するクラスです。
    """

    class Code1(Exception):
        """エラーコード１のエラーを発生させる内部クラスです。

        Args:
            Exception (Exception): Exception
        """
        def __init__(self):
            self._msg = error_code_map["009.001"]

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

    class Else(Exception):
        """本クラスの外部クラス内にないエラーを発生させたい場合はこちらを利用します。

        Args:
            msg ([str]): 表示させたいエラーメッセージ
        """
        def __init__(self, msg):
            self._msg = msg

        @property
        def msg(self):
            return self._msg

        def __str__(self):
            return str(self._msg)

RobotExceptions       = (RobotException.Code1,
                         RobotException.Code2,
                         RobotException.Code3,
                         RobotException.Code4,
                         RobotException.Code5,
                         RobotException.TimeOut,
                         RobotException.ValueError,
                         RobotException.Else)

DepthCameraExceptions = (DepthCameraException.Code1,
                         DepthCameraException.Code2,
                         DepthCameraException.Code3,
                         DepthCameraException.Code4,
                         DepthCameraException.Code5,
                         DepthCameraException.Else)

USBCameraExceptions    = (USBCameraException.Code1,
                          USBCameraException.Else)

LoadersExceptions      = (LoadersException.Code1,
                          LoadersException.Code2,
                          LoadersException.Code3,
                          LoadersException.Code4,
                          LoadersException.Code5,
                          LoadersException.Code6,
                          LoadersException.Code7,
                          LoadersException.Code8,
                          LoadersException.Code9,
                          LoadersException.Code10,
                          LoadersException.Code11,
                          LoadersException.Else)


TrayBinExceptions      = (TrayBinException.Code1,
                          TrayBinException.Code2,
                          TrayBinException.Code3,
                          TrayBinException.Code4,
                          TrayBinException.Code5,
                          TrayBinException.Else)

MassScaleExceptions    = (MassScaleException.Code1,
                          MassScaleException.Code2,
                          MassScaleException.Code3,
                          MassScaleException.Else)


QRExceptions           = (QRException.Code1,
                          QRException.Code2,
                          QRException.Code3,
                          QRException.Else)

DeliverablesExceptions = (DeliverablesException.Code1,
                          DeliverablesException.Code2,
                          DeliverablesException.Code3,
                          DeliverablesException.Else)
AIExceptions           = (AIException.Code1,
                          AIException.Else)

if __name__ == "__main__":
    def func1():
        raise RobotException.Code1()

    def func2():
        raise RobotException.Code2()

    def func3():
        raise DepthCameraException.Code1()

    def func4():
        raise DepthCameraException.Else("WWW")


    try:
        func2()

    except (RobotExceptions) as e:
        print(e)

    except (DepthCameraExceptions) as e:
        print(e)

    except (DeliverablesException.Code1,
            DeliverablesException.Code2,
            DeliverablesException.Code3,
            DeliverablesException.Else) as e:
        print(e)

print("End")

