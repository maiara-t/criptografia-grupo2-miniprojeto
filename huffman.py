import heapq
from collections import Counter, namedtuple


class HuffmanNode(namedtuple("Node", ["char", "freq", "left", "right"])):
    def __lt__(self, other):
        return self.freq < other.freq


class Huffman:
    def __init__(self):
        self.tree = None
        self.codes = {}

    def build_tree(self, data):
        frequency = Counter(data)
        heap = [HuffmanNode(char, freq, None, None) for char, freq in frequency.items()]
        heapq.heapify(heap)

        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            merged = HuffmanNode(None, left.freq + right.freq, left, right)
            heapq.heappush(heap, merged)

        self.tree = heap[0] if heap else None
        return self.tree

    def build_codes(self, node=None, prefix=""):
        if node is None:
            return

        if node.char is not None:
            self.codes[node.char] = prefix
        else:
            self.build_codes(node.left, prefix + "0")
            self.build_codes(node.right, prefix + "1")

    def encode(self, data):
        if isinstance(data, bytes):
            data = list(data)
        elif isinstance(data, str):
            data = list(data)

        self.tree = None
        self.codes = {}

        self.build_tree(data)
        self.build_codes(self.tree)

        encoded_text = ''.join(self.codes[char] for char in data)
        return encoded_text

    def decode(self, encoded_text):
        result = []
        node = self.tree
        for bit in encoded_text:
            node = node.left if bit == "0" else node.right
            if node.char is not None:
                result.append(node.char)
                node = self.tree

        if isinstance(result[0], int):
            return bytes(result)
        else:
            return ''.join(result)
