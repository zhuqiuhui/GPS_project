import django


def replaceDate(targetDate):
    l = list(targetDate)
    l[4] = '/'
    l[7] = '/'
    newDateStr = ''.join(l)
    return newDateStr

if __name__ == '__main__':
    s = '2017-10-01'
    print(replaceDate(s))