from pathlib import Path
import csv
from collections import defaultdict
import re
import random


def randomize_n_group(deck, shuffle=True):
    yinpa = ['ཡིན།', 'རེད།', 'རེད་འདུག']
    yopa = ['ཡོད།', 'ཡོད་རེད།', 'འདུག']
    yinsare = ['ཡིན་ས་ཡོད།', 'ཡིན་ས་རེད།', 'ཡིན་བགྱི་རེད།']
    yosare = ['ཡོད་ས་ཡོད།', 'ཡོད་ས་རེད།', 'ཡོད་བགྱི་རེད།']
    decks = defaultdict(list)
    for card in deck:
        decks['total'].append(card)
        form = card[1]
        if form in yinpa:
            decks['yinpa'].append(card)
        elif form in yopa:
            decks['yopa'].append(card)
        elif form in yinsare:
            decks['yinsare'].append(card)
        elif form in yosare:
            decks['yosare'].append(card)

    if shuffle:
        for deck, cards in decks.items():
            random.shuffle(cards)
    return decks


def prepare_flashcards(expanded, config, lang):
    cards = []
    for form, entries in expanded.items():
        for cat, sents in entries.items():
            if cat == 'dag':
                pro = config[lang][0][1][0]
                filename = f'{lang}_{form}_{pro}'
                for sent in sents:
                    card = (filename, form, sent, pro)
                    cards.append(card)
            if cat == 'zhen_anim':
                for num, sent in enumerate(sents):
                    pro = config[lang][0][1][num+1]
                    filename = f'{lang}_{form}_{pro}'
                    card = (filename, form, sent, pro)
                    cards.append(card)
            if cat == 'zhen_inanim':
                ab = {0: 'a', 1: 'b'}
                for num, sent in enumerate(sents):
                    filename = f'{lang}_{form}_inanimate_{ab[num]}'
                    card = (filename, form, sent, 'inanimate')
                    cards.append(card)
    return cards


def expand_entries(parsed, config):
    expanded = defaultdict(dict)
    for form, entries in parsed.items():
        for cat, entry in entries.items():
            if cat != 'form' and cat != 'alt':  # alternative meanings not implemented for the moment
                expanded[form][cat] = list()
            if cat == 'dag':
                expanded[form][cat].append(entry)
            if cat == 'zhen_anim':
                sents = []
                for lang, exprs in config['to_expand']:
                    for expr in exprs:
                        expr, col = expr.split(':')
                        col = int(col)-1
                        if expr in entry:
                            a, b = entry.split(expr)
                            for i in range(1, len(config[lang][0][1])):
                                pronoun = config[lang][0][1][i]
                                verb = config[lang][col][1][i]
                                sent = f'{a}{pronoun} {verb}{b}'
                                sents.append(sent)
                expanded[form][cat].extend(sents)
            if cat == 'zhen_inanim':
                if '}/{' in entry:
                    start, a, b, end = re.split(r'\{([^{]+)\}\/\{([^}]+)\}', entry)
                    expanded[form][cat].extend([f'{start}{a}{end}', f'{start}{b}{end}'])
                else:
                    expanded[form][cat].append(entry)
    return expanded


def parse_infiles(infile):
    parsed = defaultdict(dict)
    with open(infile) as file:
        tsv = list(csv.reader(file, delimiter='\t'))
        for i in range(1, len(tsv[0])):
            form = tsv[0][i]
            dag = tsv[1][i]
            zhen_anim = tsv[2][i]
            zhen_inanim = tsv[3][i]
            alt = tsv[4][i]
            parsed[form] = {'form': form, 'dag': dag, 'zhen_anim': zhen_anim, 'zhen_inanim': zhen_inanim, 'alt': alt}

    config = defaultdict(list)
    with open(Path('input/conjugation_tables.csv')) as file:
        tsv = list(csv.reader(file, delimiter='\t'))
        for i in range(1, len(tsv[0])):
            lang, cat = tsv[0][i].split('_')
            a = tsv[1][i]
            b = tsv[2][i]
            c = tsv[3][i]
            d = tsv[4][i]
            e = tsv[5][i]
            f = tsv[6][i]
            g = tsv[7][i]
            h = tsv[8][i]
            j = tsv[9][i]
            config[lang].append((cat, [a, b, c, d, e, f, g, h, j]))

        for i in range(1, len(tsv[11])):
            if tsv[11][i]:
                lang = tsv[11][i]
                to_expand = [tsv[12][i], tsv[13][i], tsv[14][i], tsv[15][i]]
                config['to_expand'].append((lang, to_expand))

        for i in range(1, 10):
            a = tsv[i][0]
            config['pronouns_bo'].append(a)

    return parsed, config


if __name__ == '__main__':
    infile = Path('input/Auxilaries and Conjugation - drills.tsv')
    parsed, config = parse_infiles(infile)
    lang = 'EN'
    expanded = expand_entries(parsed, config)
    cards_raw = prepare_flashcards(expanded, config, lang)
    decks = randomize_n_group(cards_raw, config)
    # print in csv file
    out = []
    for card in cards_raw:
        out.append('\t'.join(card))
    out = '\n'.join(out)
    Path('cards_raw.tsv').write_text(out)

    # MEMRISE LESSONS
    # print randomized in csv file. without filename
    # pronouns in Tibetan
    pro_table = {config['EN'][0][1][i]: config['pronouns_bo'][i] for i in range(len(config['pronouns_bo']))}
    pro_table['inanimate'] = 'it (inanimate)'
    rand_out = []
    for cat, cards in decks.items():
        rand_out.append('\t'.join([cat, ' ', ' ']))
        rand_out.append('\t'.join([' ', ' ', ' ']))
        for card in cards:
            card = list(card)[1:]
            if card[2] in pro_table:
                card[2] = pro_table[card[2]]
            card[1] = card[1].replace('[', '').replace(']', '')
            rand_out.append('\t'.join(card))
    rand_out = '\n'.join(rand_out)
    Path('cards_raw_randomized.tsv').write_text(rand_out)
    print()
