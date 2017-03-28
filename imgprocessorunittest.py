import unittest
import imgprocessor
import time
import numpy as np

class imgprocessorunittest(unittest.TestCase):

    def GivenSizeAndBandwidthGenerateImage(self):
        img = imgprocessor()
        items = 10
        tim1 = time.time()
        for i in range(items):
            start = time.time()
            ind = np.random.randint(1, 6, 1)
            if ind == 1:
                expname = 'pictdkfwm101_3.jpg'
                name = img.generate("pictdkfwm101.jpg", 720, '2g')
                self.assertTrue(expname==name)
            elif ind == 2:
                expname = 'pictdkfwm101_6.jpg'
                img.generate("pictdkfwm101.jpg", 1600, '4g')
                self.assertTrue(expname == name)
            elif ind == 3:
                expname = 'pictdkfwm101_4.jpg'
                img.generate("pictdkfwm101.jpg", 900, '3g')
                self.assertTrue(expname == name)
            elif ind == 4:
                expname = 'pictdkfwm101_2.jpg'
                img.generate("pictdkfwm101.jpg", bandwidth='2g')
                self.assertTrue(expname == name)
            else:
                expname = 'pictdkfwm101_3.jpg'
                img.generate("pictdkfwm101.jpg", size=1600)
                self.assertTrue(expname == name)
            end = time.time()
            print('Timetaken for {} is {}'.format(ind, end - start))
        print('Printing for {} items took {} ticks'.format(items, time.time() - tim1))


if __name__ == '__main__':
    unittest.main()