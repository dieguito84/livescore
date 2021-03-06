from livescore import LiveScore

TOP5_NATIONAL_LEAGUES = ["England - Premier League", "Italy - Serie A", "Spain - LaLiga LaLiga Santander", "Germany - Bundesliga", "France - Ligue 1"]
UEFA_CLUB_LEAGUES = ["Champions League", "Europa League"]

# TODO: add argparse

# TODO: use functions 

ls = LiveScore()
homepage = ls.get_html()

all_leagues = homepage.find("div[class='row row-tall'][data-type='stg']") + homepage.find("div[class='row row-tall mt4']")

for l in all_leagues:
    league = l.text.split("\n")
    # league[0] = 'paese - campionato'(England - Premier League) oppure 'competizione - stage'(Europa League - Quarter-finals), league[1] = 'Mese giorno' (April 19)
    league_title = league[0]
    if league_title in TOP5_NATIONAL_LEAGUES or any(x in league[0] for x in UEFA_CLUB_LEAGUES):
        print("\n- " + league_title)
        print(70 * "-")
        all_matches = homepage.find("a[data-stg-id='{}']".format(l.attrs["data-stg-id"]))
        for m in all_matches:
            match = m.text.split("\n")
            # match[0] = 'orario'(21:00)(prima della partita) oppure 'minuto'(88')(durante la partita) oppure 'FT'(dopo la partita), match[1] = 'Limited coverage', match[2] = 'squadra in casa', match[3] = 'risultato(1 - 0)', match[4] = 'squadra fuori casa'
            match_time = match[0]
            match_home_team = match[2]
            match_away_team = match[4]
            match_result = match[3]
            print("{:>5} {:>25} {} {}".format(match_time, match_home_team, match_result, match_away_team))
            match_partial_url = m.attrs["href"]
            match_page = ls.get_html(match_partial_url)
            match_events = (match_page.find("[data-type=incident]"))    # CSS selector - contiene solo eventi di tipo incident
            for event in match_events:
                event_goal = event.find("svg[class='inc goal']")    # contiene solo eventi goal
                event_own_goal = event.find("svg[class='inc goal-own']")    # contiene solo eventi autogoal
                event_penalty_goal = event.find("svg[class='inc goal-pen']")    # contiene solo eventi penaly goal
                if event_goal:    # filtra solo goals
                    event_goal_min = event.find("div[class=min]")[0].text
                    event_goal_partial_score = event.find("span[class=score]")[0].text
                    if event.find("div.tright[data-type=home] > span[data-type=player-name]")[0].text:   # se marcatore home
                        event_goal_home_scorer = event.find("span[data-type=player-name]")[0].text
                        if len(event_goal_home_scorer) > 4:    # to prevent index out of range for player name <= 4 characters
                            if event_goal_home_scorer[4] == ".":
                                event_goal_home_scorer = event_goal_home_scorer[6:]
                            elif event_goal_home_scorer[1] == ".":
                                event_goal_home_scorer = event_goal_home_scorer[3:]
                        print("{:>5} {:>25} {}".format(event_goal_min, event_goal_home_scorer, event_goal_partial_score))
                    else:    # altrimenti marcatore away
                        event_goal_away_scorer = event.find("span[data-type=player-name]")[1].text
                        if len(event_goal_away_scorer) > 4:    # to prevent index out of range for player name <= 4 characters
                            if event_goal_away_scorer[4] == ".":
                                event_goal_away_scorer = event_goal_away_scorer[6:]
                            elif event_goal_away_scorer[1] == ".":
                                event_goal_away_scorer = event_goal_away_scorer[3:]
                        print("{:>5} {:>31} {}".format(event_goal_min, event_goal_partial_score, event_goal_away_scorer))
                elif event_own_goal:    # filtra solo auto goals
                    event_own_goal_min = event.find("div[class=min]")[0].text
                    event_own_goal_partial_score = event.find("span[class=score]")[0].text
                    if event.find("div.tright[data-type=home] > span[data-type=player-name]")[0].text:   # se marcatore home
                        event_own_goal_home_scorer = event.find("span[data-type=player-name]")[0].text
                        if len(event_own_goal_home_scorer) > 4:    # to prevent index out of range for player name <= 4 characters
                            if event_own_goal_home_scorer[4] == ".":
                                event_own_goal_home_scorer = event_own_goal_home_scorer[6:]
                            elif event_own_goal_home_scorer[1] == ".":
                                event_own_goal_home_scorer = event_own_goal_home_scorer[3:]
                        print("{:>5} {:>25} {}".format(event_own_goal_min, "(OG) " + event_own_goal_home_scorer, event_own_goal_partial_score))
                    else:    # altrimenti marcatore away
                        event_own_goal_away_scorer = event.find("span[data-type=player-name]")[1].text
                        if len(event_own_goal_away_scorer) > 4:    # to prevent index out of range for player name <= 4 characters
                            if event_own_goal_away_scorer[4] == ".":
                                event_own_goal_away_scorer = event_own_goal_away_scorer[6:]
                            elif event_own_goal_away_scorer[1] == ".":
                                event_own_goal_away_scorer = event_own_goal_away_scorer[3:]
                        print("{:>5} {:>31} {}".format(event_own_goal_min, event_own_goal_partial_score, "(OG) " + event_own_goal_away_scorer))
                elif event_penalty_goal:    # filtra solo penalty goals
                    event_penalty_goal_min = event.find("div[class=min]")[0].text
                    event_penalty_goal_partial_score = event.find("span[class=score]")[0].text
                    if event.find("div.tright[data-type=home] > span[data-type=player-name]")[0].text:   # se marcatore home
                        event_penalty_goal_home_scorer = event.find("span[data-type=player-name]")[0].text
                        if len(event_penalty_goal_home_scorer) > 4:    # to prevent index out of range for player name <= 4 characters
                            if event_penalty_goal_home_scorer[4] == ".":
                                event_penalty_goal_home_scorer = event_penalty_goal_home_scorer[6:]
                            elif event_penalty_goal_home_scorer[1] == ".":
                                event_penalty_goal_home_scorer = event_penalty_goal_home_scorer[3:]
                        print("{:>5} {:>25} {}".format(event_penalty_goal_min, "(PEN) " + event_penalty_goal_home_scorer, event_penalty_goal_partial_score))
                    else:    # altrimenti marcatore away
                        event_penalty_goal_away_scorer = event.find("span[data-type=player-name]")[1].text
                        if len(event_penalty_goal_away_scorer) > 4:    # to prevent index out of range for player name <= 4 characters
                            if event_penalty_goal_away_scorer[4] == ".":
                                event_penalty_goal_away_scorer = event_penalty_goal_away_scorer[6:]
                            elif event_penalty_goal_away_scorer[1] == ".":
                                event_penalty_goal_away_scorer = event_penalty_goal_away_scorer[3:]
                        print("{:>5} {:>31} {}".format(event_penalty_goal_min, event_penalty_goal_partial_score, "(PEN) " + event_penalty_goal_away_scorer))
            print("")
        print(70 * "-")