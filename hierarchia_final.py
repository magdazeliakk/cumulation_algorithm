from topoly import *
import re

def subknots_cumulation(knots: dict, all_babies: dict):
    '''
    Sumowanie prawdopodobieństw węzłów w podwęzłach.
    :param knots: słownik z typami węzła (str) jako kluczami oraz wartościami
    prawdopodobieństwa (float) jako wartościami
    :param all_babies: słownik z typami węzłów (str) jako kluczami oraz zbiorem
    prapodwęzłów (str) im odpowiadających
    :return subknots: słownik, gdzie kluczami są prapodwęzły (str), a wartościami
    skumulowane wartości prawdopodobieństw (float)
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
    Dodawanie orginalnych prawdopodobieństw do węzłów.
    :param knots: słownik z typami węzła (str) jako kluczami oraz wartościami
    prawdopodobieństwa (float) jako wartościami
    :param subknots: słownik, gdzie kluczami są prapodwęzły (str), a wartościami
    skumulowane wartości prawdopodobieństw (float)
    :return all_knots: słownik z typami węzła (str) jako kluczami oraz sumowanymi wartościami
    prawdopodobieństwa (float) jako wartościami
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
    :param knots: słownik z typami węzła (str) jako kluczami oraz wartościami
    prawdopodobieństwa (float) jako wartościami
    :param c: wartość typu float określająca próg prawdopodobieństwa
    :return cutoff_knots: słownik z tymi typami węzła (str) jako kluczami oraz wartościami
    prawdopodobieństwa (float) jako wartościami, które wynosiły co najmniej tyle co podane c
    '''
    cutoff_knots = {}
    for knot in knots:
        if knots[knot] >= c:
            cutoff_knots[knot] = knots[knot]
    return cutoff_knots

def new_cumulated_knot(knots: dict, crossings: dict):
    '''
    Wybór najbardziej złożonego węzła.
    :param knots: słownik z typami węzła (str) jako kluczami oraz wartościami
    prawdopodobieństwa (float) jako wartościami
    :param crossings: słownik z liczbą skrzyżowań (int) jako kluczami oraz zbiorem
    typów węzłów (str) jako wartościami
    :return new_knot: najbardziej węzeł (str)
    :return new_prob: odpowiadająca węzłowi wartość prawdopodobieństwa (float)
    '''
    max_crossing = 0
    new_knot = '0_1'
    new_prob = 0.0
    for knot in knots:
        if crossings[knot] >= max_crossing:
            max_crossing = crossings[knot]
            new_knot = knot
            new_prob = knots[knot]
    return new_knot, new_prob

def find_max_knot(prob: dict):
    '''
    Znalezienie węzła o największej wartości prawdopodobieństwa.
    :param prob: słownik z typami węzła (str) jako kluczami oraz wartościami
    prawdopodobieństwa (float) jako wartościami
    :return max_knot: węzeł (str) o największej wartości prawdopodobieństwa
    :return max_prob: największa wartość prawdopodobieństwa (float)
    '''
    knots = prob.keys()
    max_prob = 0
    max_knot = ''
    for knot in knots:
        knot_prob = prob[knot]
        if knot_prob > max_prob :
            max_prob = knot_prob
            max_knot = knot
    return max_knot, max_prob

def cumulation_by_hierarchy(data: dict, all_babies: dict, crossings: dict, prob_cutoff: float):
    '''
    Zastosowanie algorytmu dla wartości prawdopodobieństwa dla wszystkich podłańcuchów.
    :param data: słownik zawierający na pozycji kluczy ideksy podłańcuchów, a na pozycji wartości słowniki z typami
    węzłów (str) jako kluczami oraz wartościami prawdopodobieństwa (float) jako wartościami
    :param all_babies: słownik z typami węzłów (str) jako kluczami oraz zbiorem
    prapodwęzłów (str) im odpowiadających
    :param crossings: słownik z liczbą skrzyżowań (int) jako kluczami oraz zbiorem
    typów węzłów (str) jako wartościami
    :param prob_cutoff: wartość typu float określająca próg prawdopodobieństwa
    :return t: słownik zawierający na pozycji kluczy ideksy podłańcuchów, a na pozycji wartości słowniki z typem
    węzła po skorzystaniu z algorytmu kumulacji (str) jako kluczami oraz nową wartością prawdopodobieństwa (float)
    jako wartościami
    '''
    t = '{'
    for index in data:
        index_knots = data[index]
        orginal_max_knot, orginal_max_prob = find_max_knot(index_knots)
        if orginal_max_prob <= prob_cutoff:
            subknots = subknots_cumulation(index_knots, all_babies)
            all_knots = all_knots_cumulation(index_knots, subknots)
            knots_cutoff = cutoff(all_knots, prob_cutoff)
            new_knot, new_prob = new_cumulated_knot(knots_cutoff, crossings)
            t += '%s:{\'%s\':%f},' % (index, str(new_knot), new_prob)
        else:
            t += f'{index}:{index_knots}'
    t += '}'
    return t

def cumulation_algorithm(file_path: str, prob_cutoff: float, subsubknots_path: str, crossing_path: str):
    '''
    Otwarcie potrzebnych plików do działania algorytmu, zapisanie wyników działania,
    wygenerowanie macierzy knot fingerprint.
    :param file_path: ścieżka do pliku txt zawierającego statystyki domknięć dla całego łańcucha
    :param prob_cutoff: wartość typu float określająca próg prawdopodobieństwa
    :param subsubknots_path: ścieżka do pliku txt zawierającego słownik prapodwęzłów dla każdego węzła
    :param crossing_path: ścieżka do pliku txt zawierającego liczbę skrzyżowań i typy węzłów
    :return: zapisanie wyników działania algorytmu kumulacji wartości prawdopodobieństwa, wygerenrowanie
    i zapisanie nowej macierzy knot fingerprint
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