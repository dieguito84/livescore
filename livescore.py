from requests_html import HTMLSession

BASE_URL = "https://www.livescore.com"

USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0"

TOP5_NATIONAL_LEAGUES = ["England - Premier League", "Italy - Serie A", "Spain - LaLiga LaLiga Santander", "Germany - Bundesliga", "France - Ligue 1"]
UEFA_CLUB_LEAGUES = ["Champions League", "Europa League"]

# TODO: add methods to print results and goals details
# TODO: add methods to return complete match details (result + goals) as dictionary (JSON format)
# TODO: add argparse for simple text output (short and detailed) and JSON format output (short and detailed)
# TODO: fix "Champions League" and "Europa League" filter (atm got selected also Africa/Asia/Oceania Champions League and single countries Europa League play-offs)
# TODO: add favourite team and favourite player

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

        :param homepage_html: HTML page obtained via get_html method. Required.
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
        return list(self.leagues_names_and_elements)    # nested list
    
    def matches_finder(self, homepage_html, league_html):
        '''
        Return a list containing HTML elements for every match of a league.

        :param homepage_html: HTML page obtained via get_html method. Required.
        :param league_html: HTML page obtained via leagues_finder method. Required. 
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
        self.match_partial_url = match.attrs["href"]
        return [self.match_time, self.match_home_team, self.match_away_team, self.match_result, self.match_partial_url]
    
    def event_finder(self, match_html):
        '''
        Return a list containing HTML elements for every event of a match.

        :param match_html: HTML page obtained via get_html method, using match's partial URL as parameter. Required.
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
        # TODO: add explicit else statement (return "other-event")

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

    def match_details(self, details):
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
        match_dict = {}
        match_dict["time"] = details[0]
        match_dict["home_team"] = details[1]
        match_dict["away_team"] = details[2]
        match_dict["result"] = details[3]
        return match_dict

    def goal_details(self, details):
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
        goal_dict = {}
        goal_dict["goal_type"] = details[0]
        goal_dict["min"] = details[1]
        goal_dict["partial_score"] = details[2]
        goal_dict["scorer_type"] = details[3]
        goal_dict["scorer_name"] = details[4]
        return goal_dict
    
    def match_complete_details(self):
        '''
        to define
        '''
        pass

def main():
    ls = LiveScore()
    homepage = ls.get_html()

    leagues = ls.leagues_finder(homepage)

    for matches in leagues:
        print(matches[0])
        print(ls.matches_finder(homepage, matches[1]))
        for i in range(len(ls.matches_finder(homepage, matches[1]))):
            print(ls.matches_finder(homepage, matches[1])[i])
            print(ls.match_parser(ls.matches_finder(homepage, matches[1])[i]))
            print(ls.match_details(ls.match_parser(ls.matches_finder(homepage, matches[1])[i])))    # print match details json format test
            match_page = ls.get_html(ls.match_parser(ls.matches_finder(homepage, matches[1])[i])[4])
            print(match_page)
            print(ls.event_finder(match_page))
            for incident in ls.event_finder(match_page):
                print(ls.goal_finder(incident))
                if ls.goal_finder(incident) is not None:    # to exclude None object coming from goal_finder (implicit else)
                    # TODO: add management of explicit else statement (if ls.goal_finder(incident) is not "other-event")
                    print(ls.goal_parser(ls.goal_finder(incident)[0], ls.goal_finder(incident)[1]))
                    print(ls.goal_details(ls.goal_parser(ls.goal_finder(incident)[0], ls.goal_finder(incident)[1])))    # print goal details json format test

if __name__ == "__main__":
    main()