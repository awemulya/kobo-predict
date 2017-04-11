from collections import OrderedDict


class BarGenerator(object):
    def __init__(self, sites):
        self.data = OrderedDict()
        self.data['0-10'] = 0
        self.data['10-20'] = 0
        self.data['20-30'] = 0
        self.data['30-40'] = 0
        self.data['40-50'] = 0
        self.data['50-60'] = 0
        self.data['60-70'] = 0
        self.data['70-80'] = 0
        self.data['80-90'] = 0
        self.data['90-100'] = 0
        for site in sites:
            progress_range = self.get_range(site.progress())
            self.data[progress_range] +=1

    def get_range(self, progress):
        if progress in range(0,10): return self.data.keys()[0]
        if progress in range(10,20): return self.data.keys()[1]
        if progress in range(20,30): return self.data.keys()[2]
        if progress in range(30,40): return self.data.keys()[3]
        if progress in range(40,50): return self.data.keys()[4]
        if progress in range(50,60): return self.data.keys()[5]
        if progress in range(60,70): return self.data.keys()[6]
        if progress in range(70,80): return self.data.keys()[7]
        if progress in range(80,90): return self.data.keys()[8]
        if progress in range(90,101): return self.data.keys()[9]
