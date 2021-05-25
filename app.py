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
    "Halbic": "FF568E"
}
con = sqlite3.connect('data.db')
cur = con.cursor()
cur.execute('SELECT * FROM Languages')
langs = {}
for i in cur.fetchall():
    langs[i[0]] = list(i)
for i in langs:
    if langs[i][5] in ['MIA', 'OIA'] or 'Old' in langs[i][1]:
        langs[i].append(f"""<svg viewBox="0 0 30 30" xmlns="http://www.w3.org/2000/svg">
  <polygon points="0,15 15,0 30,15 15,30" fill="#{colors[langs[i][5]]}" stroke="black" stroke-width="2"/>
</svg>""")
    else:
        langs[i].append(f"""<svg viewBox="0 0 30 30" xmlns="http://www.w3.org/2000/svg">
  <circle cx="14" cy="14" r="13" fill="#{colors[langs[i][5]]}" stroke="black" stroke-width="2"/>
</svg>""")

@app.route("/")
def hello_world():
    return render_template('index.html')

@app.route("/reflexes")
def reflexes():
    page = int(request.args.get('page', 1))
    con = sqlite3.connect('data.db')
    cur = con.cursor()
    cur.execute('SELECT * FROM Reflexes limit ?, ?', (page * 200 - 200, 200))
    return render_template('reflex.html', langs=langs, colors=colors, reflexes=cur.fetchall(), page=page)

@app.route("/languages")
@app.route("/languages/<lang>")
def languages(lang=None):
    if lang:
        page = int(request.args.get('page', 1))
        con = sqlite3.connect('data.db')
        cur = con.cursor()
        # cur.execute('SELECT * FROM Reflexes WHERE language=?', (lang,))
        cur.execute('SELECT * FROM Reflexes WHERE language=? limit ?, ?', (lang, page * 200 - 200, 200))
        return render_template('reflex.html', lang=lang, langs=langs, colors=colors, reflexes=cur.fetchall(), page=page)
    else:
        return render_template('langs.html', langs=langs, colors=colors)

@app.route("/entries")
@app.route('/entries/<entry>')
@app.route('/entries/<entry>/<lang>')
def entries(entry=None, lang=None):
    page = int(request.args.get('page', 1))
    print(entry, lang, page)
    con = sqlite3.connect('data.db')
    cur = con.cursor()
    if entry:
        if lang:
            cur.execute('SELECT * FROM Reflexes WHERE entry=? AND language=?', (entry, lang))
            return render_template('reflex.html', lang=lang, langs=langs, colors=colors, entry=entry, reflexes=cur.fetchall())
        else:
            print('individual', str(entry))
            cur.execute('SELECT * FROM Entries WHERE number=?', (entry,))
            entry_info = cur.fetchall()[0]

            cur.execute('SELECT * FROM Reflexes WHERE entry=?', (entry,))
            reflexes = cur.fetchall()
            ref = {}
            for reflex in reflexes:
                if reflex[1] not in ref: ref[reflex[1]] = []
                ref[reflex[1]].append(reflex)
            print(ref)
            return render_template('entry.html', entry=entry_info, reflexes=ref, langs=langs, colors=colors)
    else:
        print('all')
        cur.execute('SELECT * FROM Entries limit ?, ?', (page * 200 - 200, 200))
        return render_template('entries.html', entries=cur.fetchall(), page=page)

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)