from requests_html import HTMLSession

url = "https://www.livescore.com/soccer/live/"

user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0"

top_leagues = ["England - Premier League", "Italy - Serie A", "Spain - LaLiga Santander", "Germany - Bundesliga", "France - Ligue 1"]

session = HTMLSession()
page = session.get(url, headers={"User-Agent": user_agent})
page.html.render()

#test = page.html.find("div[class='row row-tall'][data-type='stg']")
for league in top_leagues:
    if league in page.html.find("div[class='row row-tall'][data-type='stg']")[0].text.split("\n"):
        print(page.html.find("div[class='row row-tall'][data-type='stg']")[0].text.split("\n"))
        print(page.html.find("a[data-stg-id='{}']".format(page.html.find("div[class='row row-tall'][data-type='stg']")[0].attrs["data-stg-id"]))[0].text.split("\n"))
#for t in test:
#    print(t.text)
    #print(t.attrs)
    #attrib = t.attrs["data-stg-id"]
#    print(page.html.find("a[data-stg-id='{}']".format(t.attrs["data-stg-id"]))[0].text)

test2 = page.html.find("div[class='row row-tall mt4']")
for t in test2:
    for league in top_leagues:
        if league in t.text.split("\n")[0]:
            print(t.text.split("\n"))
            print(page.html.find("a[data-stg-id='{}']".format(t.attrs["data-stg-id"]))[0].text.split("\n"))