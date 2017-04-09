from collections import OrderedDict

d = OrderedDict()
d['0-10'] = 0
d['10-20'] = 0
d['20-30'] = 0
d['30-40'] = 0
d['40-50'] = 0
d['50-60'] = 0
d['60-70'] = 0
d['70-80'] = 0
d['80-90'] = 0
d['90-100'] = 0


def get_range(progress):
    if progress in range(0,10): return d.keys()[0]
    if progress in range(10,20): return d.keys()[1]
    if progress in range(20,30): return d.keys()[2]
    if progress in range(30,40): return d.keys()[3]
    if progress in range(40,50): return d.keys()[4]
    if progress in range(50,60): return d.keys()[5]
    if progress in range(60,70): return d.keys()[6]
    if progress in range(70,80): return d.keys()[7]
    if progress in range(80,90): return d.keys()[8]
    if progress in range(90,101): return d.keys()[9]


class BarGenerator(object):
    def __init__(self, sites):
        self.data = d
        for site in sites:
            progress_range = get_range(site.progress())
            self.data[progress_range] +=1
