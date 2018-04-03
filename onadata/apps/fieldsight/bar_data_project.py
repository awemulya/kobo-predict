from collections import OrderedDict


class BarGenerator(object):
    def __init__(self, sites):
        self.data = OrderedDict()
        self.data['Unstarted'] = 0
        self.data['< 20'] = 0
        self.data['20 - 40'] = 0
        self.data['40 - 60'] = 0
        self.data['60 - 80'] = 0
        self.data['80 <'] = 0
        self.data['Completed'] = 0

        for site in sites:
            progress_range = self.get_range(site.progress())
            self.data[progress_range] +=1

    def get_range(self, progress):
        if progress == 0: return self.data.keys()[0]
        if progress in range(1,20): return self.data.keys()[1]
        if progress in range(20,40): return self.data.keys()[2]
        if progress in range(40,60): return self.data.keys()[3]
        if progress in range(60,80): return self.data.keys()[4]
        if progress in range(80,100): return self.data.keys()[5]
        if progress == 100: return self.data.keys()[6]
