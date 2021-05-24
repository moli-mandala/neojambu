import unidecode

with open('a.txt', 'r') as fin:
    for row in fin.readlines():
        a = list(row.strip().split(','))
        a[0] = unidecode.unidecode(a[0])
        print(','.join(a))