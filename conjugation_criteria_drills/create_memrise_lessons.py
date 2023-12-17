from pathlib import Path
import csv
from collections import defaultdict


def parse_in_cats(parsed, cats):
    # order: form, meaning, modality, category

    # ordering entries
    lessons = defaultdict(list)
    by_cats = defaultdict(list)
    by_cats_neg = defaultdict(list)
    for entry in parsed.values():
        current = [entry['form'], entry['meaning'], entry['modality'], entry['category'], ' ']
        neg = [entry['negative'], entry['meaning'], entry['modality'], entry['category'], 'negative']
        if current[3] == 'Verb':
            lessons['verbs'].append(current)
            lessons['neg_verbs'].append(neg)
        if current[3] == 'Past':
            lessons['past'].append(current)
            lessons['neg_past'].append(neg)
        if current[3] == 'Present':
            lessons['present'].append(current)
            lessons['neg_present'].append(neg)
        if current[3] == 'Future':
            lessons['future'].append(current)
            lessons['neg_future'].append(neg)
        if current[3] == 'Conditional':
            lessons['conditional'].append(current)
            lessons['neg_conditional'].append(neg)

        for cat, entries in cats.items():
            if cat == 'meaning':
                for e in entries:
                    if current[1] == e:
                        by_cats[e].append(current)
                        by_cats_neg[e].append(neg)
            if cat == 'mod':
                for e in entries:
                    if current[2] == e:
                        by_cats[e].append(current)
                        by_cats_neg[e].append(neg)

    # preparing for export
    out = []
    for a in [lessons, by_cats, by_cats_neg]:
        for cat, entries in a.items():
            out.append(f'\n# {cat}')
            out.append('\n'.join(['\t'.join(e) for e in entries]))
    out = '\n'.join(out)
    return out


def parse_in_file(infile):
    parsed = defaultdict(dict)
    with open(infile) as file:
        tsv = list(csv.reader(file, delimiter='\t'))
        for i in range(1, len(tsv[0])):
            meaning = tsv[0][i]
            form = tsv[1][i]
            neg = tsv[2][i]
            cat = tsv[3][i]
            mod = tsv[4][i]
            parsed[form] = {'meaning': meaning, 'form': form, 'negative': neg, 'category': cat, 'modality': mod}

        # list options
        cats = {}
        cats['meaning'] = sorted(list(set(tsv[0][1:])))
        cats['cat'] = sorted(list(set(tsv[3][1:])))
        cats['mod'] = sorted(list(set(tsv[4][1:])))
        out = []
        for cat, entries in cats.items():
            out.append(cat)
            out.append('\t'+'\n\t'.join(entries))
        out = '\n'.join(out)
        Path('cats.txt').write_text(out)

    return parsed, cats


if __name__ == '__main__':
    infile = Path('input/Auxilaries and Conjugation.tsv')
    parsed, cats = parse_in_file(infile)
    out = parse_in_cats(parsed, cats)
    Path('lessons.tsv').write_text(out)
