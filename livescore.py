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
        self.session = HTMLSession()
        self.page = self.session.get(BASE_URL + partial_url, headers={"User-Agent": user_agent})
        self.page.html.render()
        return self.page.html
    
    def leagues_finder(self, page):
        '''
        Returns a nested list where each element is a tuple containing
        league title and HTML page as <class 'requests_html.HTML'> object.

        [(England - Premier League, requests_html.HTML), (Italy - Serie A, requests_html.HTML), ...]

        :param page: HTML page obtained via get_html method. Required.
        '''
        self.all_leagues = page.find("div[class='row row-tall'][data-type='stg']") + page.find("div[class='row row-tall mt4']")
        self.leagues_names = []
        self.leagues_elements = []
        for l in self.all_leagues:
            self.league = l.text.split("\n")
            # league[0] = 'paese - campionato'(England - Premier League) oppure 'competizione - stage'(Europa League - Quarter-finals), league[1] = 'Mese giorno' (April 19)
            self.league_title = self.league[0]
            if self.league_title in TOP5_NATIONAL_LEAGUES or any(x in self.league[0] for x in UEFA_CLUB_LEAGUES):
                self.leagues_names.append(self.league_title)
                self.leagues_elements.append(l)
        self.leagues_names_and_elements = zip(self.leagues_names, self.leagues_elements)
        return self.leagues_names_and_elements    # nested list
    
    def matches_finder(self, page, league):
        '''
        Returns a list containing HTML elements for every match of a league.

        :param page: HTML page obtained via get_html method. Required.
        :param league: HTML page obtained via leagues_finder method. Required. 
        '''
        self.all_matches = page.find("a[data-stg-id='{}']".format(league.attrs["data-stg-id"]))
        return self.all_matches
    
    def match_parser(self, match):
        pass
    
    def event_finder(self, match_page):
        '''
        Returns a list containing HTML elements for every event of a match.

        :param page: HTML page obtained via get_html method. Required.
        :param league: HTML page obtained via leagues_finder method. Required. 
        '''
        self.match_events = match_page.find("[data-type=incident]")    # CSS selector - contiene solo eventi di tipo incident
        return self.match_events
    
    def goal_finder(self, event):
        if event.find("svg[class='inc goal']"):
            return ["goal", event]
        elif event.find("svg[class='inc goal-own']"):
            return ["goal-own", event]
        elif event.find("svg[class='inc goal-pen']"):
            return ["goal-pen", event]

    def goal_parser(self, goal):
        self.goal_min = goal.find("div[class=min]")[0].text
        self.goal_partial_score = goal.find("span[class=score]")[0].text
        if goal.find("div.tright[data-type=home] > span[data-type=player-name]")[0].text:   # se marcatore home
            self.goal_home_scorer = goal.find("span[data-type=player-name]")[0].text
            if self.goal_home_scorer[4] == ".":
                self.goal_home_scorer = self.goal_home_scorer[6:]
            elif self.goal_home_scorer[1] == ".":
                self.goal_home_scorer = self.goal_home_scorer[3:]
        else:    # altrimenti marcatore away
            self.goal_away_scorer = goal.find("span[data-type=player-name]")[1].text
            if self.goal_away_scorer[4] == ".":
                self.goal_away_scorer = self.goal_away_scorer[6:]
            elif self.goal_away_scorer[1] == ".":
                self.goal_away_scorer = self.goal_away_scorer[3:]

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