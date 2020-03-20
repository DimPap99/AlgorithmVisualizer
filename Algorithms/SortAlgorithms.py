def swap(array, index1, index2):
    temp = array[index1]
    array[index1] = array[index2]
    array[index2] = temp
    return array


def insertionSort(num_array):
    swaps = []

    # iterate over the array by starting from 1
    for i in range(1, len(num_array)):
        j = i
        # j will be equal to i and each time we will check if the previous j --- > j - 1 is larger than
        # the current j if it is we swap it and decrease the index j by one.This is repeated until j is <0 or the previous
        # index, j - 1 doesnt have a larger value than index j. (arr[j-1] < arr[j] ---> stops)
        while j > 0 and num_array[j - 1] > num_array[j]:
            num_array = swap(num_array, j, j - 1)
            swaps.append([j, j - 1])
            j -= 1
    # print(num_array)
    return swaps


def partition(num_array, low, high,swaps):
    pivot = num_array[high]
    index = low

    for j in range(low, high):
        if num_array[j] < pivot:

            num_array[index], num_array[j] = num_array[j], num_array[index]
            swaps.append([index, j])
            index += 1
    num_array[index], num_array[high] = num_array[high], num_array[index]
    swaps.append([index, high])
    print(swaps)
    return index

def quickSort(num_array, low, high,swaps):

    if low < high:
        pivot = partition(num_array, low, high,swaps)

        quickSort(num_array, low, pivot - 1,swaps)
        quickSort(num_array, pivot + 1, high,swaps)

def bubbleSort(num_array):
    swaps = []
    for i in range(len(num_array)):
        for j in range(0, len(num_array) - i - 1):
            if num_array[j] < num_array[j+1]:
                num_array[j], num_array[j+1] = num_array[j+1], num_array[j]
                swaps.append([j,j+1])

    return swaps
