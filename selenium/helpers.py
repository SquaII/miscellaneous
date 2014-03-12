#-*- coding:utf8 -*-


def read_config():
    temp = []
    config_dict = {}
    read_next = True
    stripped = ', '
    with open("config") as config_file:
        for line in config_file:
            line = line.strip()
            if line and line[0] != "#":
                if read_next:
                    parts = line.partition("=")
                    key = parts[0].strip(stripped)
                    temp.append(parts[2].strip(stripped))
                else:
                    temp.append(line.strip(stripped))
                if line[-1] == ",":
                    read_next = False
                else:
                    read_next = True
                    config_dict.update({key: temp})
                    temp = []
    return config_dict


def helper(seq_len):
    a = [[True], [False]]
    for i in xrange(seq_len):
        temp = []
        length = len(a)
        for j in xrange(length):
            tmp1 = a[j][:]
            tmp2 = a[j][:]
            tmp1.append(True)
            tmp2.append(False)
            temp.append(tmp1)
            temp.append(tmp2)
        a = temp[:]
    return a


def time_formatter(time_lists):
    output = ""
    for t_list in time_lists:
        output += t_list.pop(0)
        average = sum(t_list) / len(t_list)
        output += "    Количество прогонов: {0}\n".format(len(t_list))
        output += "    Среднее время: {0:.2f}.\n".format(average)
        output += "    Минимальное время: {0:.2f}.\n".format(min(t_list))
        output += "    Максимальное время: {0:.2f}.\n".format(max(t_list))
    return output
