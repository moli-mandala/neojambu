import sqlite3
import csv
import os
from unicodedata import normalize

os.remove('data.db')

con = sqlite3.connect('data.db')
cur = con.cursor()

clade = {}

cur.execute('CREATE TABLE Languages (id TEXT, name TEXT, glottocode TEXT, long TEXT, lat TEXT, clade TEXT)')
with open('cldf/languages.csv', 'r') as fin:
    entries = csv.reader(fin)
    for i, row in enumerate(entries):
        if i == 0: continue
        row = [normalize('NFC', x) for x in row]
        clade[row[0]] = row[5]
        cur.execute('INSERT INTO Languages VALUES (?, ?, ?, ?, ?, ?)', tuple(row))

cur.execute('CREATE TABLE Entries (number TEXT, headword TEXT, description TEXT)')

entry_name = {}
with open('cldf/parameters.csv', 'r') as fin:
    entries = csv.reader(fin)
    for i, row in enumerate(entries):
        if i == 0: continue
        row = [normalize('NFC', x) for x in row]
        entry_name[row[0]] = row[1]
        cur.execute('INSERT INTO Entries (number, headword, description) VALUES (?, ?, ?)', (str(row[0]), str(row[1]), str(row[3])))

cur.execute('CREATE TABLE Reflexes (number TEXT, language TEXT, entry TEXT, form TEXT, gloss TEXT, native TEXT, phonemic TEXT, cognateset TEXT, notes TEXT, source TEXT, entryTitle TEXT)')

lang_map = {}
entry_map = {}
entry_clade = {}

with open('cldf/forms.csv', 'r') as fin:
    entries = csv.reader(fin)
    for i, row in enumerate(entries):
        if i == 0: continue
        row = [normalize('NFC', x) for x in row]

        for entry in row[2].split(';'):
            for entry in entry.split('+'):
                if row[1] not in lang_map: lang_map[row[1]] = 0
                lang_map[row[1]] += 1
                if entry not in entry_map: entry_map[entry] = 0
                entry_map[entry] += 1
                
                temp = row
                row[2] = entry

                data = tuple(temp + [entry_name[entry]])

                if entry not in entry_clade:
                    entry_clade[entry] = set()
                entry_clade[entry].add(clade[data[1]])

                # print(row, len(row))
                cur.execute('INSERT INTO Reflexes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', data)

cur.execute('ALTER TABLE Languages ADD count TEXT')
for lang in lang_map:
    cur.execute('UPDATE Languages SET count=? WHERE id=?', (lang_map[lang], lang))

cur.execute('ALTER TABLE Entries ADD count TEXT')
for entry in entry_map:
    cur.execute('UPDATE Entries SET count=? WHERE number=?', (entry_map[entry], entry))

cur.execute('ALTER TABLE Entries ADD clades TEXT')
for entry in entry_clade:
    cur.execute('UPDATE Entries SET clades=? WHERE number=?', (','.join(entry_clade[entry]), entry))

con.commit()
con.close()