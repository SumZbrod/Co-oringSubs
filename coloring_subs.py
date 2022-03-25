import pandas as pd
import pickle
import requests
from time import sleep
import re
import spacy
nlp = spacy.load("ja_ginza")
import platform



def load_str(path):
    with open(path) as f:
        return f.read()

class PaitSub:
    def __init__(self, n_level=4):
        self.n_level = n_level
        self.g_stat  = [] 
        self.rg_stat = [] 
        self.v_stat  = [] 
        for n in range(5, n_level-1, -1):
            self.g_stat.append(load_str(f'ndata{slesh_line}n{n}G').splitlines())    
            self.rg_stat.append(load_str(f'ndata{slesh_line}n{n}Gr').splitlines())   
            self.v_stat.append(load_str(f'ndata{slesh_line}n{n}V').splitlines())    
        self.g_palette = ['#fafa6e', '#f7ca3d', '#f09819', '#e3630e', '#d01919'][:5-n_level+1]
        self.v_palette = ['#82fa6e', '#00deb9', '#00b7ff', '#0082ff', '#6f19d0'][:5-n_level+1]

    def coloring(self, corpus):
        new_corpus = ''
        g_count = [0] * (6-self.n_level)
        v_count = [0] * (6-self.n_level)
        for line in corpus.splitlines():
            if len(line)>1 and not line.isnumeric() and '-->' not in line:
                # print(line)
                line = line.replace('…', 'ð')
                doc = nlp(line)
                new_line = ''
                for token in doc.to_json()['tokens']:
                    # print(token['tag'], end=' ')
                    # print('\t', token['morph'])
                    phrase = line[token['start']: token['end']]
                    lemma = token['lemma']
                    for n in range(6-self.n_level):
                        if lemma in self.g_stat[n]:
                            # print(lemma)
                            lemma = f'<font color="{self.g_palette[n]}">{phrase}</font>'
                            g_count[n] += 1
                            break
                        elif lemma in self.v_stat[n]:
                            v_count[n] += 1
                            # print(lemma)
                            lemma = f'<font color="{self.v_palette[n]}">{phrase}</font>'
                            break
                    new_line += lemma
                for n in range(6-self.n_level):
                    for r_g in self.rg_stat[n]:
                        # print(r_g)
                        for part in re.findall(r_g, new_line):
                            new_line = new_line.replace(part, f'<font color="{self.g_palette[n]}">{part}</font>')
                            g_count[n] += 1
                            print(part)
                new_line = new_line.replace('ð', '…')
                

            else:
                new_line = line
            new_corpus += new_line + '\n'
        print('grammar: ', g_count)
        print('vocabulary: ', v_count)
        return new_corpus

def main():
    if platform.system() == 'Linux':
        slesh_line = '/'
    else:
        slesh_line = '\\'

    # str_path = '/home/nikita/Downloads/Sono_Bisque_Doll_wa_Koi_wo_Suru/My.Dress-Up.Darling.S01E06.WEBRip.Netflix.ja[cc].srt'
    str_path = input('path to the srt subtitles: ')
    # str_path = '/home/nikita/Downloads/n/1-26/10.srt'
    str_path = str_path + slesh_line
    str_data = load_str(str_path)

    P = PaitSub(3)

    new_corpus = P.coloring(str_data)

    new_path =  str_path[:-4] + 'c.srt'
    # print(new_path)
    with open(new_path, 'w') as f:
        f.write(new_corpus)


if __name__ == '__main__':
    main() 