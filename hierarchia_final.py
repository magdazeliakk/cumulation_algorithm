from topoly import *
import re

def subknots_cumulation(knots: dict, all_babies: dict):
    '''
    Sumowanie prawdopodobieństw węzłów w podwęzłach.
    '''
    subknots = {}
    for knot in knots:
        if knot in all_babies:
            for subknot in all_babies[knot]:
                if subknot in subknots:
                    subknots[subknot] += knots[knot]
                else:
                    if knots[knot] != 0:
                        subknots[subknot] = knots[knot]
    return subknots

def all_knots_cumulation(knots: dict, subknots: dict):
    '''
    Dodawanie orginalnych prawdopodobieństw do podwęzłów.
    '''
    all_knots = {}
    for knot in knots:
        if knot in subknots:
            if knot in all_knots:
                all_knots[knot] += subknots[knot]
            else:
                all_knots[knot] = subknots[knot]

            all_knots[knot] += knots[knot]
        else:
            if knot in all_knots:
                all_knots[knot] += knots[knot]
            else:
                all_knots[knot] = knots[knot]
    return all_knots

def cutoff(knots: dict, c: float):
    '''
    Wybór kandydatów na lidera w węźle ze względu na próg prawdopodbieństwa.
    '''
    cutoff_knots = {}
    for knot in knots:
        if knots[knot] >= c:
            cutoff_knots[knot] = knots[knot]
    return cutoff_knots

def new_cumulated_knot(knots: dict, crossings: dict):
    '''
    Wybór najbardziej złożonego węzła.
    '''
    max_crossing = 0
    new_knot = '0_1'
    new_prob = 0.0
    for knot in knots:
        if crossings[knot] > max_crossing:
            max_crossing = crossings[knot]
            new_knot = knot
            new_prob = knots[knot]
    return new_knot, new_prob

def cumulation_by_hierarchy(data: dict, all_babies: dict, crossings: dict, prob_cutoff: float):
    '''
    Zastosowanie algorytmu dla wartości prawdopodobieństwa dla wszytskich podłańcuchów.
    '''
    t = '{'
    for index in data:
        index_knots = data[index]
        subknots = subknots_cumulation(index_knots, all_babies)
        all_knots = all_knots_cumulation(index_knots, subknots)
        knots_cutoff = cutoff(all_knots, prob_cutoff)
        new_knot, new_prob = new_cumulated_knot(knots_cutoff, crossings)
        t += '%s:{\'%s\':%f},' % (index, str(new_knot), new_prob)
    t += '}'
    return t

def cumulation_algorithm(file_path: str, prob_cutoff: float, subsubknots_path: str, crossing_path: str):
    '''
    Otwarcie potrzebnych plików do działania algorytmu, zapisanie wyników działania,
    wygenerowanie macierzy knot fingerprint.
    '''
    file_ssk = open(subsubknots_path, 'r')
    subsubknots = file_ssk.read()
    subsubknots = eval(subsubknots)

    numbers_of_crossings = open(crossing_path, 'r')
    numbers_of_crossings = numbers_of_crossings.read()
    numbers_of_crossings = numbers_of_crossings.split('\n')
    numbers_of_crossings = [crossing.split(' --> ') for crossing in numbers_of_crossings]
    crossings = {}
    for c in numbers_of_crossings:
        knots = c[1].split(', ')
        for k in knots:
            crossings[k] = int(c[0])
    file_d = open(file_path, 'r')
    data = file_d.read()
    data = re.sub('8_20\|3_1#3_1', '8_20', data)
    data = eval(data)

    t = cumulation_by_hierarchy(data, subsubknots, crossings, prob_cutoff)
    n_data = open(file_path+'after_cumulation.txt', 'w')
    n_data.write(t)
    n_data.close()

    plot_matrix(file_path+'after_cumulation.txt', map_cutoff=prob_cutoff,
                map_filename=file_path+'after_cumulation',
                map_arrows=False)