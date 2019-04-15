from requests_html import HTMLSession

#url = "https://www.livescore.com/soccer/live/"
url = "https://www.livescore.com/"

user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0"

top5_national_leagues = ["England - Premier League", "Italy - Serie A", "Spain - LaLiga LaLiga Santander", "Germany - Bundesliga", "France - Ligue 1"]
uefa_club_leagues = ["Champions League", "Europa League"]

session = HTMLSession()
page = session.get(url, headers={"User-Agent": user_agent})
page.html.render()

all_leagues = (page.html.find("div[class='row row-tall'][data-type='stg']")) + (page.html.find("div[class='row row-tall mt4']"))

for l in all_leagues:
    league = l.text.split("\n")
    if league[0] in top5_national_leagues:
        print("\n- " + league[0] + "\n------------------------------")
        all_matches = page.html.find("a[data-stg-id='{}']".format(l.attrs["data-stg-id"]))
        for m in all_matches:
            match = m.text.split("\n")
            print("{} {} {}".format(match[2], match[3], match[4]))
        print("------------------------------")