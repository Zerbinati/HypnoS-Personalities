def line_to_pgn(line, white, black, result):
    return '[White "{}"]\n[Black "{}"] \n[Result "{}"]\n\n{}{}\n\n'.format(white, black, result, line, result)
  
with open('cerebellum.pgn', 'w') as outf:
    first_line = True
    with open('white-moves.txt', 'r') as inf:
        for line in inf:
            if first_line:
                first_line = False
                continue
            line = line.replace('{100%}', '')
            outf.write(line_to_pgn(line[line.index(':')+2:-1], 'SF', 'other', '1-0'))
    first_line = True
    with open('black-moves.txt', 'r') as inf:
        for line in inf:
            if first_line:
                first_line = False
                continue
            line = line.replace('{100%}', '')
            outf.write(line_to_pgn(line[line.index(':')+2:-1], 'other', 'SF', '0-1'))
            
with open('cerebellum-white.pgn', 'w') as outf:
    first_line = True
    with open('white-moves.txt', 'r') as inf:
        for line in inf:
            if first_line:
                first_line = False
                continue
            line = line.replace('{100%}', '')
            outf.write(line_to_pgn(line[line.index(':')+2:-1], 'SF', 'other', '1-0'))
            
with open('cerebellum-black.pgn', 'w') as outf:
    first_line = True
    with open('black-moves.txt', 'r') as inf:
        for line in inf:
            if first_line:
                first_line = False
                continue
            line = line.replace('{100%}', '')
            outf.write(line_to_pgn(line[line.index(':')+2:-1], 'other', 'SF', '0-1'))
