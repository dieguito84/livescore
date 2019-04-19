from requests_html import HTMLSession

url = "https://www.livescore.com/"
#url = "https://www.livescore.com/soccer/2019-04-18/"

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
    league_title = league[0]
    if league_title in top5_national_leagues or any(x in league[0] for x in uefa_club_leagues):
        print("\n- " + league_title + "\n------------------------------")
        all_matches = page.html.find("a[data-stg-id='{}']".format(l.attrs["data-stg-id"]))
        for m in all_matches:
            match = m.text.split("\n")
            # match[0] = 'orario'(21:00)(prima della partita) oppure 'minuto'(88')(durante la partita) oppure 'FT'(dopo la partita), match[1] = 'Limited coverage', match[2] = 'squadra in casa', match[3] = 'risultato(1 - 0)', match[4] = 'squadra fuori casa'
            match_time = match[0]
            match_home_team = match[2]
            match_away_team = match[4]
            match_result = match[3]
            print("{} {} {} {}".format(match_time, match_home_team, match_result, match_away_team))
            url2 = "https://www.livescore.com" + m.attrs["href"]
            session2 = HTMLSession()
            page2 = session2.get(url2, headers={"User-Agent": user_agent})
            page2.html.render()
            match_events = (page2.html.find("[data-type=incident]"))    # CSS selector
            for event in match_events:
                event_goal = event.find("svg[class='inc goal']")    # contiene solo eventi goal
                event_own_goal = event.find("svg[class='inc goal-own']")    # contiene solo eventi autogoal
                event_penalty_goal = event.find("svg[class='inc goal-pen']")    # contiene solo eventi penaly goal
                if event_goal:    # filtra solo goals
                    event_goal_min = event.find("div[class=min]")[0].text
                    event_goal_partial_score = event.find("span[class=score]")[0].text
                    if event.find("span[class=visible-inline-xxs]"):   # check esistenza short name
                        event_goal_home_scorer = event.find("span[data-type=player-name]")[0].text[3:]    # strip short name
                        event_goal_away_scorer = event.find("span[data-type=player-name]")[1].text[3:]    # strip short name
                    else:
                        event_goal_home_scorer = event.find("span[data-type=player-name]")[0].text
                        event_goal_away_scorer = event.find("span[data-type=player-name]")[1].text
                    if event_goal_home_scorer:
                        print("{} {} {}".format(event_goal_min, event_goal_home_scorer, event_goal_partial_score))
                    else:
                        print("{} {} {}".format(event_goal_min, event_goal_partial_score, event_goal_away_scorer))
                elif event_own_goal:    # filtra solo auto goals
                    event_own_goal_min = event.find("div[class=min]")[0].text
                    event_own_goal_partial_score = event.find("span[class=score]")[0].text
                    if event.find("span[class=visible-inline-xxs]"):   # check esistenza short name
                        event_own_goal_home_scorer = event.find("span[data-type=player-name]")[0].text[3:]    # strip short name
                        event_own_goal_away_scorer = event.find("span[data-type=player-name]")[1].text[3:]    # strip short name
                    else:
                        event_own_goal_home_scorer = event.find("span[data-type=player-name]")[0].text
                        event_own_goal_away_scorer = event.find("span[data-type=player-name]")[1].text
                    if event_own_goal_home_scorer:
                        print("{} {} {} {}".format(event_own_goal_min, "(OG)", event_own_goal_home_scorer, event_own_goal_partial_score))
                    else:
                        print("{} {} {} {}".format(event_own_goal_min, event_own_goal_partial_score, "(OG)", event_own_goal_away_scorer))
                elif event_penalty_goal:    # filtra solo penalty goals
                    event_penalty_goal_min = event.find("div[class=min]")[0].text
                    event_penalty_goal_partial_score = event.find("span[class=score]")[0].text
                    if event.find("span[class=visible-inline-xxs]"):   # check esistenza short name
                        event_penalty_goal_home_scorer = event.find("span[data-type=player-name]")[0].text[3:]    # strip short name
                        event_penalty_goal_away_scorer = event.find("span[data-type=player-name]")[1].text[3:]    # strip short name
                    else:
                        event_penalty_goal_home_scorer = event.find("span[data-type=player-name]")[0].text
                        event_penalty_goal_away_scorer = event.find("span[data-type=player-name]")[1].text
                    if event_penalty_goal_home_scorer:
                        print("{} {} {} {}".format(event_penalty_goal_min, "(PEN)", event_penalty_goal_home_scorer, event_penalty_goal_partial_score))
                    else:
                        print("{} {} {} {}".format(event_penalty_goal_min, event_penalty_goal_partial_score, "(PEN)", event_penalty_goal_away_scorer))
            print("")
        print("------------------------------")