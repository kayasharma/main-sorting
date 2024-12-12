from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os
import time

# Create Flask application instance
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)
socketio = SocketIO(app)

# Serve the index.html file when accessing the root URL
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

# Define the sorting endpoint
@app.route('/sort', methods=['POST'])
def sort_array():
    array = request.json.get('array', [])
    algorithm = request.json.get('algorithm', 'bubble')
    
    if algorithm == 'bubble':
        sorted_array, metrics = bubble_sort(array, algorithm)
    elif algorithm == 'insertion':
        sorted_array, metrics = insertion_sort(array, algorithm)
    elif algorithm == 'quicksort':
        sorted_array, metrics = quick_sort(array, 0, len(array) - 1, algorithm)
    elif algorithm == 'merge':
        sorted_array, metrics = merge_sort(array, algorithm)
    elif algorithm == 'heap':
        sorted_array, metrics = heap_sort(array, algorithm)
    elif algorithm == 'radix':
        sorted_array, metrics = radix_sort(array, algorithm)
    elif algorithm == 'bucket':
        sorted_array, metrics = bucket_sort(array, algorithm)
    elif algorithm == 'counting':
        sorted_array, metrics = counting_sort(array, algorithm)
    else:
        return jsonify({'error': 'Unknown sorting algorithm'}), 400

    return jsonify({'sortedArray': sorted_array, 'metrics': metrics})

# Bubble sort algorithm implementation with real-time updates and metrics
def bubble_sort(arr, algorithm):
    n = len(arr)
    comparisons = swaps = 0
    for i in range(n):
        for j in range(0, n - i - 1):
            comparisons += 1
            if arr[j] > arr[j + 1]:
                swaps += 1
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                socketio.emit('array update', {'array': arr, 'algorithm': algorithm})
                time.sleep(0.5)
    metrics = {'comparisons': comparisons, 'swaps': swaps}
    return arr, metrics

# Insertion sort algorithm implementation with real-time updates and metrics
def insertion_sort(arr, algorithm):
    comparisons = swaps = 0
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and key < arr[j]:
            comparisons += 1
            swaps += 1
            arr[j + 1] = arr[j]
            j -= 1
            socketio.emit('array update', {'array': arr, 'algorithm': algorithm})
            time.sleep(0.5)
        arr[j + 1] = key
        comparisons += 1  # Make sure to count the final comparison where key >= arr[j]
        socketio.emit('array update', {'array': arr, 'algorithm': algorithm})
        time.sleep(0.5)
    metrics = {'comparisons': comparisons, 'swaps': swaps}
    return arr, metrics


# Quick sort algorithm implementation with real-time updates and metrics
def quick_sort(arr, low, high, algorithm):
    comparisons = swaps = 0
    if low < high:
        pi, comps, swps = partition(arr, low, high, algorithm)
        comparisons += comps
        swaps += swps
        left_sorted, left_metrics = quick_sort(arr, low, pi - 1, algorithm)
        right_sorted, right_metrics = quick_sort(arr, pi + 1, high, algorithm)
        comparisons += left_metrics['comparisons'] + right_metrics['comparisons']
        swaps += left_metrics['swaps'] + right_metrics['swaps']
    metrics = {'comparisons': comparisons, 'swaps': swaps}
    return arr, metrics

def partition(arr, low, high, algorithm):
    pivot = arr[high]
    comparisons = swaps = 0
    i = low - 1
    for j in range(low, high):
        comparisons += 1
        if arr[j] < pivot:
            i += 1
            swaps += 1
            arr[i], arr[j] = arr[j], arr[i]
            socketio.emit('array update', {'array': arr, 'algorithm': algorithm})
            time.sleep(0.5)
    swaps += 1
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    socketio.emit('array update', {'array': arr, 'algorithm': algorithm})
    time.sleep(0.5)
    return i + 1, comparisons, swaps

# Merge sort algorithm implementation with real-time updates and metrics
def merge_sort(arr, algorithm):
    comparisons = swaps = 0
    if len(arr) > 1:
        mid = len(arr) // 2
        left_half, left_metrics = merge_sort(arr[:mid], algorithm)
        right_half, right_metrics = merge_sort(arr[mid:], algorithm)
        i = j = k = 0
        comparisons += left_metrics['comparisons'] + right_metrics['comparisons']
        swaps += left_metrics['swaps'] + right_metrics['swaps']
        while i < len(left_half) and j < len(right_half):
            comparisons += 1
            if left_half[i] < right_half[j]:
                swaps += 1
                arr[k] = left_half[i]
                i += 1
            else:
                swaps += 1
                arr[k] = right_half[j]
                j += 1
            k += 1
            socketio.emit('array update', {'array': arr, 'algorithm': algorithm})
            time.sleep(0.5)
        while i < len(left_half):
            swaps += 1
            arr[k] = left_half[i]
            i += 1
            k += 1
            socketio.emit('array update', {'array': arr, 'algorithm': algorithm})
            time.sleep(0.5)
        while j < len(right_half):
            swaps += 1
            arr[k] = right_half[j]
            j += 1
            k += 1
            socketio.emit('array update', {'array': arr, 'algorithm': algorithm})
            time.sleep(0.5)
    metrics = {'comparisons': comparisons, 'swaps': swaps}
    return arr, metrics

# Heap sort algorithm implementation with real-time updates and metrics
def heap_sort(arr, algorithm):
    comparisons = swaps = 0
    def heapify(arr, n, i):
        nonlocal comparisons, swaps
        largest = i
        l = 2 * i + 1
        r = 2 * i + 2
        comparisons += 1
        if l < n and arr[l] > arr[largest]:
            largest = l
        comparisons += 1
        if r < n and arr[r] > arr[largest]:
            largest = r
        if largest != i:
            swaps += 1
            arr[i], arr[largest] = arr[largest], arr[i]
            heapify(arr, n, largest)
            socketio.emit('array update', {'array': arr, 'algorithm': algorithm})
            time.sleep(0.5)
    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)
    for i in range(n - 1, 0, -1):
        swaps += 1
        arr[i], arr[0] = arr[0], arr[i]
        heapify(arr, i, 0)
        socketio.emit('array update', {'array': arr, 'algorithm': algorithm})
        time.sleep(0.5)
    metrics = {'comparisons': comparisons, 'swaps': swaps}
    return arr, metrics

# Radix sort algorithm implementation with real-time updates and metrics
def radix_sort(arr, algorithm):
    comparisons = swaps = 0
    def counting_sort(arr, exp):
        nonlocal comparisons, swaps
        n = len(arr)
        output = [0] * n
        count = [0] * 10
        for i in range(n):
            index = arr[i] // exp
            count[(index % 10)] += 1
        for i in range(1, 10):
            count[i] += count[i - 1]
        i = n - 1
        while i >= 0:
            index = arr[i] // exp
            output[count[(index % 10)] - 1] = arr[i]
            count[(index % 10)] -= 1
            i -= 1
        for i in range(len(arr)):
            arr[i] = output[i]
            socketio.emit('array update', {'array': arr, 'algorithm': algorithm})
            time.sleep(0.5)
    max1 = max(arr)
    exp = 1
    while max1 / exp > 0:
        counting_sort(arr, exp)
        exp *= 10
    metrics = {'comparisons': comparisons, 'swaps': swaps}
    return arr, metrics

# Bucket sort algorithm implementation with real-time updates and metrics
def radix_sort(arr, algorithm):
    comparisons = swaps = 0

    def counting_sort(arr, exp):
        nonlocal comparisons, swaps
        n = len(arr)
        output = [0] * n
        count = [0] * 10

        # Count occurrences
        for i in range(n):
            index = arr[i] // exp
            count[index % 10] += 1

        # Update count positions
        for i in range(1, 10):
            count[i] += count[i - 1]

        # Build the output array
        i = n - 1
        while i >= 0:
            index = arr[i] // exp
            output[count[index % 10] - 1] = arr[i]
            count[index % 10] -= 1
            i -= 1
            comparisons += 1  # Count the comparison

        # Copy the output array to arr
        for i in range(len(arr)):
            arr[i] = output[i]
            swaps += 1  # Count the swap
            socketio.emit('array update', {'array': arr, 'algorithm': algorithm})
            time.sleep(0.5)

    # Get the maximum number to know the number of digits
    max_val = max(arr)
    exp = 1
    while max_val // exp > 0:
        counting_sort(arr, exp)
        exp *= 10
        comparisons += 1  # Count the comparison for each pass through the loop

    metrics = {'comparisons': comparisons, 'swaps': swaps}
    print(f'Radix Sort Metrics: {metrics}')  # Logging
    return arr, metrics

# Bucket sort algorithm implementation with real-time updates and metrics
def counting_sort(arr, algorithm):
    comparisons = swaps = 0
    max_val = max(arr)
    m = max_val + 1
    count = [0] * m
    for a in arr:
        count[a] += 1
    i = 0
    for a in range(m):
        for c in range(count[a]):
            swaps += 1
            arr[i] = a
            i += 1
            socketio.emit('array update', {'array': arr, 'algorithm': algorithm})
            time.sleep(0.5)
    metrics = {'comparisons': comparisons, 'swaps': swaps}
    print(f'Counting Sort Metrics: {metrics}')  # Logging
    return arr, metrics

def bucket_sort(arr, algorithm):
    comparisons = swaps = 0
    bucket = []
    slot_num = 10
    for i in range(slot_num):
        bucket.append([])

    for j in arr:
        index_b = int(slot_num * j / (max(arr) + 1))
        bucket[index_b].append(j)

    for i in range(slot_num):
        bucket[i] = sorted(bucket[i])
        socketio.emit('array update', {'array': arr, 'algorithm': algorithm})
        time.sleep(0.5)

    k = 0
    for i in range(slot_num):
        for j in range(len(bucket[i])):
            swaps += 1
            arr[k] = bucket[i][j]
            k += 1
            socketio.emit('array update', {'array': arr, 'algorithm': algorithm})
            time.sleep(0.5)
    metrics = {'comparisons': comparisons, 'swaps': swaps}
    print(f'Bucket Sort Metrics: {metrics}')  # Logging
    return arr, metrics
if __name__ == '__main__': 
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)