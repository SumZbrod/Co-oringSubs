from time import sleep
import re
import spacy
import platform
import argparse
import os
nlp = spacy.load("ja_ginza")

def load_str(path):
    with open(path) as f:
        return f.read()

def get_slesh():
    if platform.system() == 'Linux':
        slesh_line = '/'
    else:
        slesh_line = '\\'
    return slesh_line

class PaintSub:
    def __init__(self, n_level=4):
        slesh_line = get_slesh()
        if slesh_line == '/':
            cwd_part = '/.config/mpv/scripts/Co-oringSubs/'
        else: 
            cwd_part = f'C:/Users/{os.getlogin()}/AppData/Roaming/mpv/scripts/Co-oringSubs'
        cwd = slesh_line.join(os.getcwd().split(slesh_line)[:3])+cwd_part
        self.n_level = n_level
        self.g_stat  = [] 
        self.rg_stat = [] 
        self.v_stat  = [] 
    
        for n in range(5, n_level-1, -1):
            self.g_stat.append(load_str( f'{cwd}ndata{slesh_line}n{n}G').splitlines())    
            self.rg_stat.append(load_str(f'{cwd}ndata{slesh_line}n{n}Gr').splitlines())   
            self.v_stat.append(load_str( f'{cwd}ndata{slesh_line}n{n}V').splitlines())    
        self.v_palette = ['#fafa6e', '#f7ca3d', '#f09819', '#e3630e', '#d01919'][:5-n_level+1]
        self.g_palette = ['#82fa6e', '#00deb9', '#00b7ff', '#0082ff', '#6f19d0'][:5-n_level+1]

        self.specs = ['…', ' ']

    def replace_spec(self, line):
        for i, s in enumerate(self.specs):
            line = line.replace(s, f'{i}ð')
        return line
    

    def dereplace_spec(self, line):
        for i, s in enumerate(self.specs):
            line = line.replace(f'{i}ð', s)
        return line


    def coloring(self, corpus, sub_ex='srt'):
        new_corpus = ''
        g_count = [0] * (6-self.n_level)
        v_count = [0] * (6-self.n_level)
        for line in corpus.splitlines():
            if sub_ex == 'srt':
                flag_preparing = len(line)>1 and not line.isnumeric() and '-->' not in line
            else:
                flag_preparing = line[:8] == 'Dialogue'
            if flag_preparing:
                if sub_ex == 'ass':
                    line = line.split(',,')[-1]
                    pre_line = ',,'.join(line.split(',,')[:-1])

                line = self.replace_spec(line)
                doc = nlp(line)
                new_line = ''
                for token in doc.to_json()['tokens']:
                    # print(token['tag'], end=' ')
                    # print('\t', token['morph'])
                    phrase = line[token['start']: token['end']]
                    token_lemma = token['lemma']
                    for n in range(6-self.n_level):
                        if token_lemma in self.g_stat[n]:
                            # print(lemma)
                            phrase = f'<font color="{self.g_palette[n]}">{phrase}</font>'
                            g_count[n] += 1
                            break
                        elif token_lemma in self.v_stat[n]:
                            v_count[n] += 1
                            # print(lemma)
                            phrase = f'<font color="{self.v_palette[n]}">{phrase}</font>'
                            break
                    new_line += phrase
                for n in range(6-self.n_level):
                    for r_g in self.rg_stat[n]:
                        # print(r_g)
                        for part in re.findall(r_g, new_line):
                            new_line = new_line.replace(part, f'<font color="{self.g_palette[n]}">{part}</font>')
                            g_count[n] += 1

                new_line = self.dereplace_spec(new_line)
            else:
                new_line = line
            if flag_preparing and sub_ex == 'ass':
                new_line = pre_line + new_line
            new_corpus += new_line + '\n'
        print('grammar: ', g_count)
        print('vocabulary: ', v_count)
        return new_corpus

def main():
    slesh_line = get_slesh()
    parser = argparse.ArgumentParser()
    parser.add_argument("subs_path")
    subs_path = parser.parse_args().subs_path
    sub_ex = subs_path[-3:]
    print(subs_path)
    if 'file://' in subs_path:
        subs_path = subs_path[7:]
    str_data = load_str(subs_path.replace('%20', ' '))

    P = PaintSub(3)

    new_corpus = P.coloring(str_data, sub_ex)

    new_path =  subs_path[:-4] + '_c.' + sub_ex
    print('new_path: ', new_path)
    with open(new_path, 'w') as f:
        f.write(new_corpus)


if __name__ == '__main__':
    main() 

