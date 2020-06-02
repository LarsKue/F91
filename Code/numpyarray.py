
import math

class numpyarray(object):
    def __init__(self, data):
        self.data = data
        self.index = 0

    def __len__(self):
        return len(self.data)

    def __mul__(self, other):
        if isinstance(other, (float, int)):
            return numpyarray([x * other for x in self.data])

        if not len(self) == len(other):
            raise ValueError("Incompatible Lengths:" + str(len(self)) + " and " + str(len(other)))

        return numpyarray([x * y for x, y in zip(self.data, other.data)])

    def __rmul__(self, other):
        return self * other

    def __add__(self, other):
        if isinstance(other, (float, int)):
            return numpyarray([x + other for x in self.data])

        if not len(self) == len(other):
            raise ValueError("Incompatible Lengths:" + str(len(self)) + " and " + str(len(other)))

        return numpyarray([x + y for x, y in zip(self.data, other.data)])

    def __sub__(self, other):
        if isinstance(other, (float, int)):
            return numpyarray([x - other for x in self.data])

        if not len(self) == len(other):
            raise ValueError("Incompatible Lengths:" + str(len(self)) + " and " + str(len(other)))

        return numpyarray([x - y for x, y in zip(self.data, other.data)])


    def __div__(self, other):
        if isinstance(other, (float, int)):
            return numpyarray([x / other for x in self.data])

        if not len(self) == len(other):
            raise ValueError("Incompatible Lengths:" + str(len(self)) + " and " + str(len(other)))

        return numpyarray([x / y for x, y in zip(self.data, other.data)])

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def append(self, item):
        self.data.append(item)

    def mean(self):
        return sum(self.data) / len(self.data)

    def __iter__(self):
        return self

    def next(self):
        if self.index >= len(self.data):
            raise StopIteration
        rv = self.data[self.index]
        self.index += 1
        return rv

    @staticmethod
    def cosh(arr):
        return numpyarray([math.cosh(x) for x in arr.data])

    @staticmethod
    def sqrt(arr):
        return numpyarray([math.sqrt(x) for x in arr.data])

    @staticmethod
    def cos(arr):
        return numpyarray([math.cos(x) for x in arr.data])

    @staticmethod
    def vectorize(f):
        def inner(*arrs, **kwargs):
            rv = numpyarray([])
            for i in range(len(arrs) - 1):
                if not len(arrs[i]) == len(arrs[i + 1]):
                    raise ValueError("Incompatible Lengths")
            # all arrays are of same length
            rv = numpyarray([f(*[arr[i] for arr in arrs], **kwargs) for i in range(len(arrs[0]))])
            # for i in range(len(arrs[0])
            #     elements = [arr[i] for arr in arrs]
            #     f_val = f(*elements, **kwargs)
            #     rv.append(f_val)
            # rv = numpyarray([f(x, *args, **kwargs) for x in arr])
            return rv
        return inner

    def __repr__(self):
        return str(self.data)
