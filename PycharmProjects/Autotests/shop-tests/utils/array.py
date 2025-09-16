def split(arr):
    if len(arr) == 1:
        return arr
    elif len(arr) % 2 == 0:
        return [arr[-round(len(arr) / 2) :], arr[: round(len(arr) / 2)]]
    else:
        return [arr[-len(arr) // 2 + 1 :], arr[: len(arr) // 2 + 1]]
