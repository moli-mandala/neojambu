import sqlite3
import csv
import os

os.remove('data.db')

con = sqlite3.connect('data.db')
cur = con.cursor()

lang_map = {}
cur.execute('CREATE TABLE Languages (id TEXT, name TEXT, glottocode TEXT, long TEXT, lat TEXT, clade TEXT)')
with open('../cldf/languages.csv', 'r') as fin:
    entries = csv.reader(fin)
    for i, row in enumerate(entries):
        if i == 0: continue
        lang_map[row[0]] = row[1]
        cur.execute('INSERT INTO Languages VALUES (?, ?, ?, ?, ?, ?)', tuple(row))

cur.execute('CREATE TABLE Entries (number TEXT, headword TEXT, description TEXT)')

with open('../cldf/parameters.csv', 'r') as fin:
    entries = csv.reader(fin)
    for i, row in enumerate(entries):
        if i == 0: continue
        cur.execute('INSERT INTO Entries (number, headword, description) VALUES (?, ?, ?)', (str(row[0]), str(row[1]), str(row[3])))

cur.execute('CREATE TABLE Reflexes (number TEXT, language TEXT, entry TEXT, form TEXT, gloss TEXT, native TEXT, phonemic TEXT, cognateset TEXT, notes TEXT, source TEXT)')

with open('../cldf/forms.csv', 'r') as fin:
    entries = csv.reader(fin)
    for i, row in enumerate(entries):
        if i == 0: continue
        row[1] = lang_map[row[1]]
        cur.execute('INSERT INTO Reflexes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', tuple(row))

con.commit()
con.close()