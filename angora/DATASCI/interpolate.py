##encoding=utf-8

"""
Copyright (c) 2015 by Sanhe Hu
------------------------------
    Author: Sanhe Hu
    Email: husanhe@gmail.com
    Lisence: LGPL
    
Compatibility
-------------
    IronPython2.7: Yes

Prerequisites
-------------
    None

Import Command
--------------
    from angora.DATASCI.interpolate import LinearInterpolator, arange
"""

import bisect

def find_lt(array, x):
    "Find rightmost item index less than x"
    i = bisect.bisect_left(array, x)
    return i-1

def find_le(array, x):
    "Find rightmost item index less than or equal to x"
    i = bisect.bisect_right(array, x)
    return i-1

def find_gt(array, x):
    "Find leftmost item index greater than x"
    i = bisect.bisect_right(array, x)
    return i

def find_ge(array, x):
    "Find leftmost item index greater than or equal to x"
    i = bisect.bisect_left(array, x)
    return i

class LinearInterpolator():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.lower = x[0]
        self.upper = x[-1]

    def __call__(self, x_new):
        """Interpolate value to new x axis. O(n) implementation
        """
        if ((x_new[0] < self.lower) or (x_new[-1] > self.upper)):
            raise ValueError
        
        ind1 = find_le(self.x, x_new[0])
        x = self.x[ind1:][::-1]
        y = self.y[ind1:][::-1]
        
        y_new = list()
        for i in x_new:
            while 1:
                try:
                    x1, y1 = x.pop(), y.pop()
                    if x1 <= i:
                        left_x = x1
                        left_y = y1
                    else:
                        right_x = x1
                        right_y = y1
                        x.append(right_x)
                        x.append(left_x)
                        y.append(right_y)
                        y.append(left_y)
                        y_new.append(self.locate(left_x, left_y, right_x, right_y, i))
                        break
                except:
                    y_new.append(left_y)
                    break
        return y_new

    def interpolate_legacy(self, x_new):
        """Interpolate value to new x axis. O(n*log(n)) implementation. Using binary
        search to find left greatest equal and right smallest value. This is a legacy
        method and don't use.
        """
        if ((x_new[0] < self.lower) or (x_new[-1] > self.upper)):
            raise ValueError
        
        y_new = list()
        for i in x_new:
            try:
                ind1 = find_le(self.x, i)
                ind2 = find_gt(self.x, i)
                x1, y1, x2, y2 = self.x[ind1], self.y[ind1], self.x[ind2], self.y[ind2]
                y_new.append(self.locate(x1, y1, x2, y2, i))
            except:
                ind1 = find_lt(self.x, i)
                ind2 = find_ge(self.x, i)
                x1, y1, x2, y2 = self.x[ind1], self.y[ind1], self.x[ind2], self.y[ind2]
                y_new.append(self.locate(x1, y1, x2, y2, i))        
        return y_new
    
    def locate(self, x1, y1, x2, y2, x3):
        """given 2 points (x1, y1), (x2, y2), find y3 for x3.
        """
        return y1 - 1.0 * (y1 - y2) * (x1 - x3) / (x1 - x2)
        
def arange(start=None, end=None, count=None, gap=None):
    """
    start, end, count
    start, end, freq
    start, count, freq
    end, count, freq
    """
    if (bool(start) + bool(end) + bool(count) + bool(gap)) != 3:
        raise Exception("Must specify three of start, end, count or gap")
    
    array = list()
    if not start:
        start = end - count * gap
        for _ in xrange(count):
            start += gap
            array.append(start)
        return array
    
    elif not end:
        start -= gap
        for _ in xrange(count):
            start += gap
            array.append(start)
        return array
    
    elif not count:
        start -= gap
        for _ in xrange(2**28):
            start += gap
            if start <= end:
                array.append(start)
            else:
                return array
                
    else:
        gap = 1.0 * (end - start) / (count - 1)
        start -= gap
        for _ in xrange(count):
            start += gap
            array.append(start)
        return array


if __name__ == "__main__":
    import unittest
    import time
    
    class LinearInterpolatorUnittest(unittest.TestCase):
        def test_functionality(self):
            x = [1,2,3]
            y = [3,2,1]
            f = LinearInterpolator(x, y)
            x_new = [1, 1.5, 2, 2.5, 3]
            y_new = f(x_new)
            self.assertListEqual(y_new, [3.0, 2.5, 2.0, 1.5, 1.0]) 
    
        def test_performance(self): # 0.155 ~ 0.165
            x = arange(start=1, end=1000000, gap=1)
            y = arange(start=1, end=1000000, gap=1)
            x_new = arange(start=1, end=1000000, gap=0.8731)
            
            st = time.clock()
            f = LinearInterpolator(x, y)
            y_new1 = f(x_new)
            print(time.clock()-st)
            
            st = time.clock()
            f = LinearInterpolator(x, y)
            y_new2 = f.interpolate_legacy(x_new)
            print(time.clock()-st)
            
            self.assertListEqual(y_new1, y_new2)
            
    class arangeUnittest():
        def test_functionality(self):
            self.assertListEqual(
                arange(end=10, count=10, gap=1),
                [1,2,3,4,5,6,7,8,9,10],
                )
            self.assertListEqual(
                arange(start=1, count=10, gap=1),
                [1,2,3,4,5,6,7,8,9,10],
                )
            self.assertListEqual(
                arange(start=1, end=10, gap=1),
                [1,2,3,4,5,6,7,8,9,10],
                )
            self.assertListEqual(
                arange(start=1, end=10, count=10),
                [1,2,3,4,5,6,7,8,9,10],
                )
            
    unittest.main()
