from Algorithms.Registry import Registry


# Every sort algorithm is a SortAlgorithm subclass with a display name, which registers it automatically.
# Subclasses implement sort() and move elements only through self.swap(), so the frontend can replay
# the recorded swaps as an animation. Usage: SortAlgorithm.get("Quick Sort")(num_array).run()
class SortAlgorithm(Registry):
    kind = "sort algorithm"

    def __init__(self, num_array):
        self.num_array = list(num_array)
        self.swaps = []

    def swap(self, index1, index2):
        if index1 != index2:
            self.num_array[index1], self.num_array[index2] = self.num_array[index2], self.num_array[index1]
            self.swaps.append([index1, index2])

    def sort(self):
        raise NotImplementedError

    # sorts a copy of the array in ascending order and returns the swaps that were made
    def run(self):
        self.sort()
        return self.swaps


# Swaps every element backwards until the previous element is not larger than it.
# Time Complexity O(n^2)
class InsertionSort(SortAlgorithm):
    name = "Insertion Sort"

    def sort(self):
        num_array = self.num_array
        for i in range(1, len(num_array)):
            j = i
            while j > 0 and num_array[j - 1] > num_array[j]:
                self.swap(j, j - 1)
                j -= 1


# Puts a pivot in its final place with smaller elements before it, then sorts both sides.
# Time Complexity O(n log n) on average
class QuickSort(SortAlgorithm):
    name = "Quick Sort"

    def sort(self):
        self.quickSort(0, len(self.num_array) - 1)

    # recurses into the smaller side and loops over the larger one, so the recursion depth stays O(log n)
    def quickSort(self, low, high):
        while low < high:
            pivot = self.partition(low, high)
            if pivot - low < high - pivot:
                self.quickSort(low, pivot - 1)
                low = pivot + 1
            else:
                self.quickSort(pivot + 1, high)
                high = pivot - 1

    # the last element is the pivot
    def partition(self, low, high):
        pivot = self.num_array[high]
        index = low
        for j in range(low, high):
            if self.num_array[j] < pivot:
                self.swap(index, j)
                index += 1
        self.swap(index, high)
        return index


# Swaps adjacent elements that are not in order; after pass i the i largest elements are in place.
# Time Complexity O(n^2)
class BubbleSort(SortAlgorithm):
    name = "Bubble Sort"

    def sort(self):
        num_array = self.num_array
        for i in range(len(num_array)):
            swapped = False
            for j in range(len(num_array) - i - 1):
                if num_array[j] > num_array[j + 1]:
                    self.swap(j, j + 1)
                    swapped = True
            if not swapped:
                break


# Keeps finding the min element of the unsorted part and moves it to the end of the sorted part.
# Time Complexity O(n^2)
class SelectionSort(SortAlgorithm):
    name = "Selection Sort"

    def sort(self):
        num_array = self.num_array
        for i in range(len(num_array)):
            min_index = i
            for j in range(i + 1, len(num_array)):
                if num_array[min_index] > num_array[j]:
                    min_index = j
            self.swap(i, min_index)


# Sorts both halves and merges them. The visualizer only animates swaps, so the halves are merged in place:
# whenever the front of the right half is smaller, it is swapped backwards to the front of the left half.
# Time Complexity O(n log n) comparisons, O(n^2) swaps
class MergeSort(SortAlgorithm):
    name = "Merge Sort"

    def sort(self):
        self.mergeSort(0, len(self.num_array) - 1)

    def mergeSort(self, low, high):
        if low < high:
            middle = (low + high) // 2
            self.mergeSort(low, middle)
            self.mergeSort(middle + 1, high)
            self.merge(low, middle, high)

    def merge(self, low, middle, high):
        left, right = low, middle + 1
        while left < right <= high:
            if self.num_array[right] < self.num_array[left]:
                for j in range(right, left, -1):
                    self.swap(j, j - 1)
                right += 1
            left += 1


# Builds a max heap, then repeatedly swaps its root (the max) to the end and restores the heap.
# Time Complexity O(n log n)
class HeapSort(SortAlgorithm):
    name = "Heap Sort"

    def sort(self):
        size = len(self.num_array)
        for i in range(size // 2 - 1, -1, -1):
            self.siftDown(i, size)
        for end in range(size - 1, 0, -1):
            self.swap(0, end)
            self.siftDown(0, end)

    # moves the element at index down until it is not smaller than its children
    def siftDown(self, index, size):
        while True:
            largest = index
            for child in (2 * index + 1, 2 * index + 2):
                if child < size and self.num_array[child] > self.num_array[largest]:
                    largest = child
            if largest == index:
                return
            self.swap(index, largest)
            index = largest


# Insertion sort over elements that are gap apart, with the gap halving down to 1.
# Time Complexity O(n^2) worst case, much faster in practice
class ShellSort(SortAlgorithm):
    name = "Shell Sort"

    def sort(self):
        num_array = self.num_array
        gap = len(num_array) // 2
        while gap > 0:
            for i in range(gap, len(num_array)):
                j = i
                while j >= gap and num_array[j - gap] > num_array[j]:
                    self.swap(j, j - gap)
                    j -= gap
            gap //= 2


# Bubble sort that alternates between forward and backward passes.
# Time Complexity O(n^2)
class CocktailShakerSort(SortAlgorithm):
    name = "Cocktail Shaker Sort"

    def sort(self):
        num_array = self.num_array
        low, high = 0, len(num_array) - 1
        swapped = True
        while swapped and low < high:
            swapped = False
            for j in range(low, high):
                if num_array[j] > num_array[j + 1]:
                    self.swap(j, j + 1)
                    swapped = True
            high -= 1
            for j in range(high, low, -1):
                if num_array[j - 1] > num_array[j]:
                    self.swap(j - 1, j)
                    swapped = True
            low += 1


# Bubble sort over elements that are gap apart, with the gap shrinking by a factor of 1.3 each pass.
# Time Complexity O(n^2) worst case, much faster in practice
class CombSort(SortAlgorithm):
    name = "Comb Sort"

    def sort(self):
        num_array = self.num_array
        gap, swapped = len(num_array), True
        while gap > 1 or swapped:
            gap = max(1, int(gap / 1.3))
            swapped = False
            for j in range(len(num_array) - gap):
                if num_array[j] > num_array[j + gap]:
                    self.swap(j, j + gap)
                    swapped = True
