def int_round(x, base=1):
    return int(base * round(float(x)/base))


def eq(value1, value2, epsilon):
    return abs(value1 - value2) < epsilon


def middle_x(bbox):
    return (bbox[0] + bbox[2])/2.
