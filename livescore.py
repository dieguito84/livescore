from requests_html import HTMLSession

BASE_URL = "https://www.livescore.com"

USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0"

TOP5_NATIONAL_LEAGUES = ["England - Premier League", "Italy - Serie A", "Spain - LaLiga LaLiga Santander", "Germany - Bundesliga", "France - Ligue 1"]
UEFA_CLUB_LEAGUES = ["Champions League", "Europa League"]

class LiveScore():
    
    def get_html(self, partial_url="", user_agent=USER_AGENT):
        '''
        Returns HTML page as <class 'requests_html.HTML'> object.

        Retrieve HTML page and renders it using requests-html library.
        It supports JavaScript.
        
        :param partial_url: partial url to add to base url (https://www.livescore.com). Optional.
        :param user_agent: browser user agent. Optional.
        '''
        self._session = HTMLSession()
        self._page = self._session.get(BASE_URL + partial_url, headers={"User-Agent": user_agent})
        self._page.html.render()
        return self._page.html
    
    def league_finder(self, homepage):
        all_leagues = homepage.find("div[class='row row-tall'][data-type='stg']") + homepage.find("div[class='row row-tall mt4']")
        for l in all_leagues:
            league = l.text.split("\n")
            # league[0] = 'paese - campionato'(England - Premier League) oppure 'competizione - stage'(Europa League - Quarter-finals), league[1] = 'Mese giorno' (April 19)
            league_title = league[0]
        if league_title in TOP5_NATIONAL_LEAGUES or any(x in league[0] for x in UEFA_CLUB_LEAGUES):
            print("\n- " + league_title)

    def event_parser(self, event):
        if event.find("svg[class='inc goal']"):
            return "goal", goal_parser(event)
        elif event.find("svg[class='inc goal-own']"):
            return "goal-own", own_goal_parser(event)
        elif event.find("svg[class='inc goal-pen']"):
            return "goal-pen", pen_goal_parser(event)

    def goal_parser(self, event):
        event_goal_min = event.find("div[class=min]")[0].text
        event_goal_partial_score = event.find("span[class=score]")[0].text
        if event.find("div.tright[data-type=home] > span[data-type=player-name]")[0].text:   # se marcatore home
            event_goal_home_scorer = event.find("span[data-type=player-name]")[0].text
            if event_goal_home_scorer[4] == ".":
                event_goal_home_scorer = event_goal_home_scorer[6:]
            elif event_goal_home_scorer[1] == ".":
                event_goal_home_scorer = event_goal_home_scorer[3:]
        else:    # altrimenti marcatore away
            event_goal_away_scorer = event.find("span[data-type=player-name]")[1].text
            if event_goal_away_scorer[4] == ".":
                event_goal_away_scorer = event_goal_away_scorer[6:]
            elif event_goal_away_scorer[1] == ".":
                event_goal_away_scorer = event_goal_away_scorer[3:]

    def own_goal_parser(self, event):
        pass

    def pen_goal_parser(self, event):
        pass

'''
example of dictionary (JSON format) to return as match result

{
    "time": "21:00" / "88'" / "FT",
    "home_team": "Juventus",
    "away_team": "Fiorentina",
    "result": "2 - 1"
}

'''

'''
example of dictionary (JSON format) to return as goal event

{
    "goal_type": "goal" / "own-goal" / "pen-goal",
    "min": "88'",
    "partial_score": "1 - 0",
    "scorer_type": "home" / "away",
    "scorer_name": "Roberto Baggio"
}

'''