from requests_html import HTMLSession

#url = "https://www.livescore.com/"
url = "https://www.livescore.com/soccer/2019-04-18/"

user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0"

top5_national_leagues = ["England - Premier League", "Italy - Serie A", "Spain - LaLiga LaLiga Santander", "Germany - Bundesliga", "France - Ligue 1"]
uefa_club_leagues = ["Champions League", "Europa League"]

session = HTMLSession()
page = session.get(url, headers={"User-Agent": user_agent})
page.html.render()

all_leagues = (page.html.find("div[class='row row-tall'][data-type='stg']")) + (page.html.find("div[class='row row-tall mt4']"))

for l in all_leagues:
    league = l.text.split("\n")
    # league[0] = 'paese - campionato'(England - Premier League) oppure 'competizione - stage'(Europa League - Quarter-finals), league[1] = 'Mese giorno' (April 19)
    if league[0] in top5_national_leagues or any(x in league[0] for x in uefa_club_leagues):
        print("\n- " + league[0] + "\n------------------------------")
        all_matches = page.html.find("a[data-stg-id='{}']".format(l.attrs["data-stg-id"]))
        for m in all_matches:
            match = m.text.split("\n")
            # match[0] = 'orario'(21:00)(prima della partita) oppure 'minuto'(88')(durante la partita) oppure 'FT'(dopo la partita), match[1] = 'Limited coverage', match[2] = 'squadra in casa', match[3] = 'risultato(1 - 0)', match[4] = 'squadra fuori casa'
            print("{} {} {}".format(match[2], match[3], match[4]))
            url2 = "https://www.livescore.com" + m.attrs["href"]
            session2 = HTMLSession()
            page2 = session2.get(url2, headers={"User-Agent": user_agent})
            page2.html.render()
            match_events = (page2.html.find("[data-type=incident]"))    # CSS selector
            #match_events = (page2.html.find("[data-type=incident] > div.min"))    # CSS selector
            for event in match_events:
                #print(event.html)
                #print(event.text.split("\n"))
                #print(event.find("svg[class='inc goal']"))
                event_goal = event.find("svg[class='inc goal']")    # contiene solo eventi goal
                event_goal_own = event.find("svg[class='inc goal-own']")    # contiene solo eventi autogoal
                if event_goal:    # filtra solo goals
                    #print(event.html)
                    #print(event.text.split("\n"))
                    #print("{} {} {} {}".format(event.find("div[class=min]")[0].text, event.find("span[data-type=player-name]")[0].text[3:], event.find("span[class=score]")[0].text, event.find("span[data-type=player-name]")[1].text[3:]))
                    #print(event.find("span[data-type=player-name]")[0].text[3:])    # remove leading short name
                    #print(event.find("span[class=score]")[0].text)
                    #print(event.html.find("div[class=min]"))
                    event_goal_min = event.find("div[class=min]")[0].text
                    event_goal_partial_score = event.find("span[class=score]")[0].text
                    event_goal_home_scorer = event.find("span[data-type=player-name]")[0].text[3:]    # senza lo short name iniziale
                    event_goal_away_scorer = event.find("span[data-type=player-name]")[1].text[3:]    # senza lo short name iniziale
                    print("{} {} {} {}".format(event_goal_min, event_goal_home_scorer, event_goal_partial_score, event_goal_away_scorer))
                elif event_goal_own:    # filtra solo auto goals
                    #print(event.html)    # todo - sistemare auto gol
                    #print(event.text.split("\n"))    # todo - sistemare auto gol
                    event_goal_own_min = event.find("div[class=min]")[0].text
                    event_goal_own_partial_score = event.find("span[class=score]")[0].text
                    event_goal_own_home_scorer = event.find("span[data-type=player-name]")[0].text[3:]    # senza lo short name iniziale
                    event_goal_own_away_scorer = event.find("span[data-type=player-name]")[1].text[3:]    # senza lo short name iniziale
                    print("{} {} {} {} {}".format(event_goal_own_min, "(OG)", event_goal_own_home_scorer, event_goal_own_partial_score, event_goal_own_away_scorer))
        print("------------------------------")