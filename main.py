from requests_html import HTMLSession

#url = "https://www.livescore.com/soccer/live/"
url = "https://www.livescore.com/"

user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0"

top_leagues = ["England - Premier League", "Italy - Serie A", "Spain - LaLiga LaLiga Santander", "Germany - Bundesliga", "France - Ligue 1"]
eu_leagues = ["Champions League", "Europa League"]

session = HTMLSession()
page = session.get(url, headers={"User-Agent": user_agent})
page.html.render()

all_leagues = []

for elem in (page.html.find("div[class='row row-tall'][data-type='stg']")):
    all_leagues.append(elem)
for elem2 in (page.html.find("div[class='row row-tall mt4']")):
    all_leagues.append(elem2)
for l in all_leagues:
    league = l.text.split("\n")
    if league[0] in top_leagues:
        print("\n- " + league[0] + "\n------------------------------")
        all_matches = page.html.find("a[data-stg-id='{}']".format(l.attrs["data-stg-id"]))
        for m in all_matches:
            match = m.text.split("\n")
            print("{} {} {}".format(match[2], match[3], match[4]))
        print("------------------------------")

"""
for league in top_leagues:
    if league in page.html.find("div[class='row row-tall'][data-type='stg']")[0].text.split("\n"):
        print(page.html.find("div[class='row row-tall'][data-type='stg']")[0].text.split("\n"))
        print(page.html.find("a[data-stg-id='{}']".format(page.html.find("div[class='row row-tall'][data-type='stg']")[0].attrs["data-stg-id"]))[0].text.split("\n"))

test2 = page.html.find("div[class='row row-tall mt4']")
for t in test2:
    for league in top_leagues:
        if league in t.text.split("\n")[0]:
            print(t.text.split("\n"))
            print(page.html.find("a[data-stg-id='{}']".format(t.attrs["data-stg-id"]))[0].text.split("\n"))
"""