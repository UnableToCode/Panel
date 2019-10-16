import re


class Interpreter:
    RESET, COLOR, SAVE, LINE, POLYGON, ELLIPSIS, CURVE, TRANSLATE, ROTATE, SCALE, CLIP = range(11)
    __pattern = list()
    __pattern.append(re.compile(r'resetCanvas (\d+) (\d+)'))
    __pattern.append(re.compile(r'setColor (\d+) (\d+) (\d+)'))
    __pattern.append(re.compile(r'saveCanvas (\w+)'))
    __pattern.append(re.compile(r'drawLine (\d+) (\d+) (\d+) (\d+) (\d+) (\w+)'))
    __pattern.append(re.compile(r'drawPolygon (\d+) (\d+) (\w+) (.+)'))
    __pattern.append(re.compile(r'drawEllipse (\d+) (\d+) (\d+) (\d+) (\d+)'))
    __pattern.append(re.compile(r'drawCurve (\d+) (\d+) ([-\w]+) (.+)'))
    __pattern.append(re.compile(r'translate (\d+) (-?\d+) (-?\d+)'))
    __pattern.append(re.compile(r'rotate (\d+) (\d+) (\d+) (-?\d+)'))
    __pattern.append(re.compile(r'scale (\d+) (\d+) (\d+) ([\d+]\.?[\d+]?)'))
    __pattern.append(re.compile(r'clip (\d+) (\d+) (\d+) (\d+) (\d+) ([-|\w]+)'))

    def interpretOrder(self, order):
        for orderType, pat in zip(range(len(self.__pattern)), self.__pattern):
            res = pat.match(order)
            if res is not None:
                args = list()
                for arg in res.groups():
                    args.append(arg)
                return InterpreterReturnItem(orderType=orderType, args=args)
        return None


class InterpreterReturnItem:
    def __init__(self, orderType, args):
        self.orderType = orderType
        self.args = args
