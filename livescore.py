from requests_html import HTMLSession

BASE_URL = "https://www.livescore.com"

USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0"

TOP5_NATIONAL_LEAGUES = ["England - Premier League", "Italy - Serie A", "Spain - LaLiga LaLiga Santander", "Germany - Bundesliga", "France - Ligue 1"]
UEFA_CLUB_LEAGUES = ["Champions League", "Europa League"]

class LiveScore():
    
    def get_html(self, partial_url="", user_agent=USER_AGENT):
        '''
        Return HTML page as <class 'requests_html.HTML'> object.

        Retrieve HTML page and renders it using requests-html library.
        It supports JavaScript.
        
        :param partial_url: partial url to add to base url (https://www.livescore.com). Optional.
        :param user_agent: browser user agent. Optional.
        '''
        self.session = HTMLSession()
        self.page = self.session.get(BASE_URL + partial_url, headers={"User-Agent": user_agent})
        self.page.html.render()
        return self.page.html
    
    def leagues_finder(self, homepage_html):
        '''
        Return a nested list where each element is a tuple containing
        league title and HTML page as <class 'requests_html.HTML'> object.

        [(England - Premier League, requests_html.HTML), (Italy - Serie A, requests_html.HTML), ...]

        :param page: HTML page obtained via get_html method. Required.
        '''
        self.all_leagues = homepage_html.find("div[class='row row-tall'][data-type='stg']") + homepage_html.find("div[class='row row-tall mt4']")
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
    
    def matches_finder(self, homepage_html, league_html):
        '''
        Return a list containing HTML elements for every match of a league.

        :param page: HTML page obtained via get_html method. Required.
        :param league: HTML page obtained via leagues_finder method. Required. 
        '''
        self.all_matches = homepage_html.find("a[data-stg-id='{}']".format(league_html.attrs["data-stg-id"]))
        return self.all_matches
    
    def match_parser(self, match):
        '''
        Return a list containing details of a match: time, home team, away team, result and match's partial url.

        [self.match_time, self.match_home_team, self.match_away_team, self.match_result, self.match_partial_url]

        :param match: single match HTML element. Required.
        '''
        self.match = match.text.split("\n")
        # match[0] = 'orario'(21:00)(prima della partita) oppure 'minuto'(88')(durante la partita) oppure 'FT'(dopo la partita), match[1] = 'Limited coverage', match[2] = 'squadra in casa', match[3] = 'risultato(1 - 0)', match[4] = 'squadra fuori casa'
        self.match_time = self.match[0]
        self.match_home_team = self.match[2]
        self.match_away_team = self.match[4]
        self.match_result = self.match[3]
        self.match_partial_url = self.match.attrs["href"]
        return [self.match_time, self.match_home_team, self.match_away_team, self.match_result, self.match_partial_url]
    
    def event_finder(self, match_html):
        '''
        Return a list containing HTML elements for every event of a match.

        :param page: HTML page obtained via get_html method. Required.
        :param league: HTML page obtained via leagues_finder method. Required. 
        '''
        self.match_events = match_html.find("[data-type=incident]")    # CSS selector - contiene solo eventi di tipo incident
        return self.match_events
    
    def goal_finder(self, event):
        '''
        Return a list containing goal type and event itself (as HTML code).

        :param event: HTML page obtained via event_finder method. Required.
        '''
        if event.find("svg[class='inc goal']"):
            return ["goal", event]
        elif event.find("svg[class='inc goal-own']"):
            return ["goal-own", event]
        elif event.find("svg[class='inc goal-pen']"):
            return ["goal-pen", event]

    def goal_parser(self, goal_type, goal):
        '''
        Return a list containing goal type, time, partial result, scorer type, scorer name.

        [goal_type, self.goal_min, self.goal_partial_score, "home", self.goal_home_scorer]

        [goal_type, self.goal_min, self.goal_partial_score, "away", self.goal_away_scorer]

        :param goal_type: "goal" or "own-goal" or "pen-goal"
        :param goal: HTML page obtained via goal_finder method. Required.
        '''
        self.goal_min = goal.find("div[class=min]")[0].text
        self.goal_partial_score = goal.find("span[class=score]")[0].text
        if goal.find("div.tright[data-type=home] > span[data-type=player-name]")[0].text:   # se marcatore home
            self.goal_home_scorer = goal.find("span[data-type=player-name]")[0].text
            if len(self.goal_home_scorer) > 4:    # to prevent index out of range for player name <= 4 characters
                if self.goal_home_scorer[4] == ".":
                    self.goal_home_scorer = self.goal_home_scorer[6:]
                elif self.goal_home_scorer[1] == ".":
                    self.goal_home_scorer = self.goal_home_scorer[3:]
            return [goal_type, self.goal_min, self.goal_partial_score, "home", self.goal_home_scorer]
        else:    # altrimenti marcatore away
            self.goal_away_scorer = goal.find("span[data-type=player-name]")[1].text
            if len(self.goal_away_scorer) > 4:    # to prevent index out of range for player name <= 4 characters
                if self.goal_away_scorer[4] == ".":
                    self.goal_away_scorer = self.goal_away_scorer[6:]
                elif self.goal_away_scorer[1] == ".":
                    self.goal_away_scorer = self.goal_away_scorer[3:]
            return [goal_type, self.goal_min, self.goal_partial_score, "away", self.goal_away_scorer]

    def match_details(self):
        '''
        Return a dictionary containing match result details.

        example of dictionary (JSON format) to return as match result

        {
            "time": "21:00" / "88'" / "FT",
            "home_team": "Juventus",
            "away_team": "Fiorentina",
            "result": "2 - 1"
        }

        '''
        pass

    def goal_details(self):
        '''
        Return a dictionary containing goal event details.

        example of dictionary (JSON format) to return as goal event

        {
            "goal_type": "goal" / "own-goal" / "pen-goal",
            "min": "88'",
            "partial_score": "1 - 0",
            "scorer_type": "home" / "away",
            "scorer_name": "Roberto Baggio"
        }

        '''
        pass