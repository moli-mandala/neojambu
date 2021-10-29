from flask import Flask, render_template, request, url_for
import sqlite3

app = Flask(__name__)

colors = {
    "Dardic": "0000FF",
    "Western Pahari": "00FFFF",
    "Central Pahari": "6F8FAF",
    "Eastern Pahari": "1434A4",
    "Lahndic": "00A36C",
    "Punjabic": "008080",
    "Sindhic": "A52A2A",
    "Gujaratic": "F0E68C",
    "Rajasthanic": "808000",
    "Marathi-Konkani": "FFAC1C",
    "Insular": "CC5500",
    "Eastern": "FF00FF",
    "Bihari": "FFC0CB",
    "Eastern Hindi": "5D3FD3",
    "Western Hindi": "51414F",
    "Migratory": "722F37",
    "MIA": "FFDEAD",
    "OIA": "E2DFD2",
    "non-IA": "FAF9F6",
    "Nuristani": "FF10F0",
    "Bhil": "93C572",
    "Halbic": "FF568E",
    "Brahui": "49796B",
    "South Dravidian I": "74C365",
    "South Dravidian II": "98FB98",
    "Central Dravidian": "29AB87",
    "North Dravidian": "4B6F44",
    "Old Dravidian": "#679267"
}
order = ['non-IA', 'Nuristani', 'Dardic', 'Western Pahari', 'Central Pahari', 'Eastern Pahari', 'Punjabic', 'Lahndic',
    'Sindhic', 'Gujaratic', 'Rajasthanic', 'Bhil', 'Marathi-Konkani', 'Halbic', 'Eastern', 'Bihari',
    'Eastern Hindi', 'Western Hindi', 'Migratory', 'Insular', 'MIA', 'OIA']
con = sqlite3.connect('data.db')
cur = con.cursor()
cur.execute('SELECT * FROM Languages')
langs = {}
for i in cur.fetchall():
    if i[6] != None:
        langs[i[0]] = list(i)
for i in langs:
    if langs[i][5] in ['MIA', 'OIA'] or 'Old' in langs[i][1]:
        langs[i].append(f"""<svg viewBox="0 0 30 30" xmlns="http://www.w3.org/2000/svg">
  <polygon points="0,15 15,0 30,15 15,30" fill="#{colors[langs[i][5]]}" stroke="black" stroke-width="2"/>
</svg>""")
    else:
        langs[i].append(f"""<svg viewBox="-2 -2 32 32" xmlns="http://www.w3.org/2000/svg">
  <circle cx="14" cy="14" r="13" fill="#{colors[langs[i][5]]}" stroke="black" stroke-width="2"/>
</svg>""")

@app.route("/")
def hello_world():
    return render_template('index.html')

@app.route("/reflexes")
@app.route("/reflexes/<reflex>")
def reflexes(reflex=None):
    con = sqlite3.connect('data.db')
    cur = con.cursor()
    if reflex:
        cur.execute('SELECT * FROM Reflexes WHERE number=?', (reflex,))
        return render_template('reflex.html', langs=langs, colors=colors, reflex=cur.fetchall()[0])
    else:
        page = int(request.args.get('page', 1))
        cur.execute('SELECT * FROM Reflexes limit ?, ?', (page * 200 - 200, 200))
        return render_template('reflexes.html', langs=langs, colors=colors, reflexes=cur.fetchall(), page=page)

@app.route("/languages")
@app.route("/languages/<lang>")
@app.route("/languages/<lang>/<lang2>")
def languages(lang=None, lang2=None):
    if lang and lang2:
        page = int(request.args.get('page', 1))
        con = sqlite3.connect('data.db')
        cur = con.cursor()
        cur.execute('SELECT * FROM Reflexes WHERE language=? ORDER BY entry*1', (lang,))
        lang_data = [(x[2], x) for x in cur.fetchall()]
        cur.execute('SELECT * FROM Reflexes WHERE language=? ORDER BY entry*1', (lang2,))
        lang2_data = [(x[2], x) for x in cur.fetchall()]
        lang_dict, lang2_dict = {}, {}

        for i in lang_data:
            if i[0] not in lang_dict: lang_dict[i[0]] = []
            lang_dict[i[0]].append(i[1])
        for i in lang2_data:
            if i[0] not in lang2_dict: lang2_dict[i[0]] = []
            lang2_dict[i[0]].append(i[1])

        both = []
        for i in lang_dict:
            if i in lang2_dict:
                both.append(i)
        return render_template('compare.html', langs=langs, colors=colors, both=both, lang=lang, lang2=lang2, lang_dict=lang_dict, lang2_dict=lang2_dict)

    elif lang:
        page = int(request.args.get('page', 1))
        con = sqlite3.connect('data.db')
        cur = con.cursor()
        # cur.execute('SELECT * FROM Reflexes WHERE language=?', (lang,))
        cur.execute('SELECT * FROM Reflexes WHERE language=? ORDER BY entry*1, entry limit ?, ?', (lang, page * 200 - 200, 200))
        return render_template('reflexes.html', lang=lang, langs=langs, colors=colors, reflexes=cur.fetchall(), page=page)
    else:
        return render_template('langs.html', langs=langs, colors=colors)

@app.route("/entries")
@app.route('/entries/<entry>')
def entries(entry=None, lang=None):
    page = int(request.args.get('page', 1))
    search = request.args.get('entry', None)
    # print(entry, lang, page)
    con = sqlite3.connect('data.db')
    cur = con.cursor()
    if entry:
        cur.execute('SELECT * FROM Entries WHERE number=?', (entry,))
        entry_info = cur.fetchall()[0]

        cur.execute('SELECT * FROM Reflexes WHERE entry=?', (entry,))
        reflexes = cur.fetchall()
        ref = {}
        for reflex in reflexes:
            if reflex[1] not in ref: ref[reflex[1]] = []
            ref[reflex[1]].append(reflex)
        # print(ref)
        return render_template('entry.html', entry=entry_info, reflexes=ref, langs=langs, colors=colors, order=order)
    else:
        if search:
            cur.execute('SELECT * FROM Entries WHERE headword LIKE ? limit ?, ?', ('%' + search + '%', page * 200 - 200, 200))
        else:
            cur.execute('SELECT * FROM Entries limit ?, ?', (page * 200 - 200, 200))
        return render_template('entries.html', entries=cur.fetchall(), page=page, colors=colors, order=order)

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)