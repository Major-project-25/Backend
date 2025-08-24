# fisher_yates_shuffle.py
import random
from typing import List, Optional, TypeVar

T = TypeVar("T")

def fisher_yates_names(names: List[T], seed: Optional[int] = None) -> List[T]:
    """
    Return a NEW list in Fisher–Yates randomized order.
    - names only (no scores)
    - set seed for reproducibility if you want
    """
    rng = random.Random(seed) if seed is not None else random
    arr = list(names)
    n = len(arr)
    for i in range(n - 1, 0, -1):
        j = rng.randint(0, i)
        arr[i], arr[j] = arr[j], arr[i]
    return arr