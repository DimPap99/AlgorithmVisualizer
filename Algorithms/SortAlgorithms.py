
def swap(array,index1,index2):
    temp = array[index1]
    array[index1] = array[index2]
    array[index2] = temp
    return array


def insertionSort(num_array):
    #iterate over the array by starting from 1
    for i in range(1,len(num_array) - 1):
        j = i
        # j will be equal to i and each time we will check if the previous j --- > j - 1 is larger than
        #the current j if it is we swap it and decrease the index j by one.This is repeated until j is <0 or the previous
        # index, j - 1 doesnt have a larger value than index j. (arr[j-1] < arr[j] ---> stops)
        while j > 0 and num_array[j-1] > num_array[j]:
            num_array = swap(num_array,j,j-1)
            print(num_array)
            j -=1
    return num_array
print(insertionSort([3,1,2,4,5]))