def sum(list):
    if list == []:
        return 0
    return list[0] + sum(list[1:])

print(sum([1,2,5, 3, 4, 5, 6, 63, 1, 43, 23, 5, 65, 34]))

def lenRec(list):
    if list == []:
        return 0
    return 1 + lenRec(list[1:])

def biggest(list):
    if len(list) == 2:
        return list[0] if list[0] > list[1] else list[1]
    sub_max = biggest(list[1:])
    return list[0] if list[0] > sub_max else sub_max

print(biggest([1, 125, 121]))