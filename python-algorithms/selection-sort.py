def findSmallest(arr):
    smallest = arr[0]
    smallest_index = 0
    count = 0
    for i in range(1, len(arr)):
        if arr[i] < smallest:
            smallest = arr[i]
            smallest_index = i
            count += 1
        count += 1
    print(count)
    return smallest_index

def selectionSort(arr):
    newArr = []
    for i in range(len(arr)):
        smallest = findSmallest(arr)
        newArr.append(arr.pop(smallest))
    return newArr

print(selectionSort([3, 7, -5, 1, 4]))    