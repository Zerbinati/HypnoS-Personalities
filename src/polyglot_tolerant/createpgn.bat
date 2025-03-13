@echo off


call polyglot_tolerant dump-book -bin book.bin -color white -out white-moves.txt
call polyglot_tolerant dump-book -bin book.bin -color black -out black-moves.txt

call convert-cerebellum.py

del white-moves.txt
del black-moves.txt