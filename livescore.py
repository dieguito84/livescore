import json

from requests_html import HTMLSession

BASE_URL = "https://www.livescore.com"

USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0"

TOP5_NATIONAL_LEAGUES = ["England - Premier League", "Italy - Serie A", "Spain - LaLiga LaLiga Santander", "Germany - Bundesliga", "France - Ligue 1"]
UEFA_CLUB_LEAGUES = ["Champions League", "Europa League"]

# TODO: add argparse for simple text output (short and detailed) and JSON format output (short and detailed)
# TODO: fix "Champions League" and "Europa League" filter (at the moment got selected also Africa/Asia/Oceania Champions League and single countries Europa League play-offs)
# TODO: add favourite team and favourite player and filter events accordingly
# TODO: create a separate Markdown file to show JSON output examples, instead of using comments in this file
# TODO: add dosctring to LiveScore class

class LiveScore():
    
    def get_html(self, partial_url="", user_agent=USER_AGENT):
        '''
        Retrieve HTML page and renders it using requests-html library.
        It supports JavaScript.
        
        :param partial_url: partial url to add to base url (https://www.livescore.com). Optional.
        :param user_agent: browser user agent. Optional.
        :returns: HTML page as <class 'requests_html.HTML'> object.
        '''
        self.session = HTMLSession()
        self.page = self.session.get(BASE_URL + partial_url, headers={"User-Agent": user_agent})
        self.page.html.render()
        return self.page.html
    
    def leagues_finder(self, homepage_html):
        '''
        Find league title and related HTML page portion
        
        Returned list example:
        [(England - Premier League, requests_html.HTML), (Italy - Serie A, requests_html.HTML), ...]

        :param homepage_html: HTML page obtained via get_html method. Required.
        :returns: nested list where each element is a tuple containing league title and HTML page as <class 'requests_html.HTML'> object.
        '''
        # TODO: find a way to show example inside the docstring in a more elegant way
        self.all_leagues = homepage_html.find("div[class='row row-tall'][data-type='stg']") + homepage_html.find("div[class='row row-tall mt4']")
        self.leagues_names = []
        self.leagues_elements = []
        for l in self.all_leagues:
            self.league = l.text.split("\n")
            # league[0] = 'country - league'(England - Premier League) or 'competition - stage'(Europa League - Quarter-finals), league[1] = 'Month day' (April 19)
            self.league_title = self.league[0]
            if self.league_title in TOP5_NATIONAL_LEAGUES or any(x in self.league[0] for x in UEFA_CLUB_LEAGUES):
                self.leagues_names.append(self.league_title)
                self.leagues_elements.append(l)
        self.leagues_names_and_elements = zip(self.leagues_names, self.leagues_elements)
        return list(self.leagues_names_and_elements)    # nested list
    
    def matches_finder(self, homepage_html, league_html):
        '''
        Find HTML elements for every match of a league.

        :param homepage_html: HTML page obtained via get_html method. Required.
        :param league_html: HTML page obtained via leagues_finder method. Required.
        :returns: list containing HTML elements for every match of a league.
        '''
        self.all_matches = homepage_html.find("a[data-stg-id='{}']".format(league_html.attrs["data-stg-id"]))
        return self.all_matches
    
    def match_parser(self, match):
        '''
        Parser for match details.
        
        Returned list example:
        [self.match_time, self.match_home_team, self.match_away_team, self.match_result, self.match_partial_url]

        :param match: single match HTML element. Required.
        :returns: list containing details of a match: time, home team, away team, result and match's partial url.
        '''
        self.match = match.text.split("\n")
        # match[0] = 'time'(21:00)(before match) or 'minute'(88')(during the match) or 'FT'(after the match), match[1] = 'Limited coverage', match[2] = 'home team', match[3] = 'result(1 - 0)', match[4] = 'away team'
        self.match_time = self.match[0]
        self.match_home_team = self.match[2]
        self.match_away_team = self.match[4]
        self.match_result = self.match[3]
        self.match_partial_url = match.attrs["href"]
        return [self.match_time, self.match_home_team, self.match_away_team, self.match_result, self.match_partial_url]
    
    def event_finder(self, match_html):
        '''
        Finds all events of a match and take related HTML elements.

        :param match_html: HTML page obtained via get_html method, using match's partial URL as parameter. Required.
        :returns: list containing HTML elements for every event of a match.
        '''
        self.match_events = match_html.find("[data-type=incident]")    # CSS selector - contains only events of type incident
        return self.match_events
    
    def goal_finder(self, event):
        '''
        Finds all events of type goal and its HTML elements.

        :param event: HTML page obtained via event_finder method. Required.
        :returns: list containing goal type and event itself (as HTML code).
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
        Parser for goal details:

        Returned lists examples:
        [goal_type, self.goal_min, self.goal_partial_score, "home", self.goal_home_scorer]

        [goal_type, self.goal_min, self.goal_partial_score, "away", self.goal_away_scorer]

        :param goal_type: "goal" or "own-goal" or "pen-goal"
        :param goal: HTML page obtained via goal_finder method. Required.
        :returns: list containing goal type, time, partial result, scorer type, scorer name.
        '''
        self.goal_min = goal.find("div[class=min]")[0].text
        self.goal_partial_score = goal.find("span[class=score]")[0].text
        if goal.find("div.tright[data-type=home] > span[data-type=player-name]")[0].text:   # if home scorer
            self.goal_home_scorer = goal.find("span[data-type=player-name]")[0].text
            if len(self.goal_home_scorer) > 4:    # to prevent index out of range for player name <= 4 characters
                if self.goal_home_scorer[4] == ".":
                    self.goal_home_scorer = self.goal_home_scorer[6:]
                elif self.goal_home_scorer[1] == ".":
                    self.goal_home_scorer = self.goal_home_scorer[3:]
            return [goal_type, self.goal_min, self.goal_partial_score, "home", self.goal_home_scorer]
        else:    # otherwise away scorer
            self.goal_away_scorer = goal.find("span[data-type=player-name]")[1].text
            if len(self.goal_away_scorer) > 4:    # to prevent index out of range for player name <= 4 characters
                if self.goal_away_scorer[4] == ".":
                    self.goal_away_scorer = self.goal_away_scorer[6:]
                elif self.goal_away_scorer[1] == ".":
                    self.goal_away_scorer = self.goal_away_scorer[3:]
            return [goal_type, self.goal_min, self.goal_partial_score, "away", self.goal_away_scorer]

    def match_details(self, details):
        '''
        Return match result details in dictionary format.

        example of dictionary (JSON format) to return as match result

        {
            "time": "21:00" / "88'" / "FT",
            "home_team": "Juventus",
            "away_team": "Fiorentina",
            "result": "2 - 1"
        }

        :param details: list containing match details. Required. Example: ['FT', 'Bologna', 'Parma', '4 - 1', '/soccer/italy/serie-a/bologna-vs-parma/6-15160337/']
        :returns: dictionary containing match result details.
        '''
        match_dict = {}
        match_dict["time"] = details[0]
        match_dict["home_team"] = details[1]
        match_dict["away_team"] = details[2]
        match_dict["result"] = details[3]
        return match_dict

    def goal_details(self, details):
        '''
        Return goal event details in dictionary format.

        example of dictionary (JSON format) to return as goal event

        {
            "goal_type": "goal" / "own-goal" / "pen-goal",
            "min": "88'",
            "partial_score": "1 - 0",
            "scorer_type": "home" / "away",
            "scorer_name": "Roberto Baggio"
        }

        :param details: list containing goal details. Required. Example: ['goal', "52'", '1 - 0', 'home', 'Riccardo Orsolini']
        :returns: dictionary containing goal event details.
        '''
        goal_dict = {}
        goal_dict["goal_type"] = details[0]
        goal_dict["min"] = details[1]
        goal_dict["partial_score"] = details[2]
        goal_dict["scorer_type"] = details[3]
        goal_dict["scorer_name"] = details[4]
        return goal_dict
    
    def match_complete_details(self, details):
        '''
        Return match results and goals details in dictionary format.

        example of dictionary (JSON format) to return as match results with goals.

        {
            "time": "21:00" / "88'" / "FT",
            "home_team": "Juventus",
            "away_team": "Fiorentina",
            "result": "2 - 1",
            "goals": [
                {
                    "goal_type": "goal" / "own-goal" / "pen-goal",
                    "min": "13'",
                    "partial_score": "1 - 0",
                    "scorer_type": "home" / "away",
                    "scorer_name": "Roberto Baggio"
                },
                {
                    "goal_type": "goal" / "own-goal" / "pen-goal",
                    "min": "26'",
                    "partial_score": "1 - 1",
                    "scorer_type": "home" / "away",
                    "scorer_name": "Roberto Baggio"
                },
                {
                    "goal_type": "goal" / "own-goal" / "pen-goal",
                    "min": "88'",
                    "partial_score": "2 - 1",
                    "scorer_type": "home" / "away",
                    "scorer_name": "Roberto Baggio"
                }
            ]
        }

        :param details: list containing match details and goal details (each goal event is a dictionary) of a single match.
        :returns: dictionary containing match results and goals details.
        '''
        match_complete_dict = {}
        match_complete_dict["time"] = details[0]
        match_complete_dict["home_team"] = details[1]
        match_complete_dict["away_team"] = details[2]
        match_complete_dict["result"] = details[3]
        match_complete_dict["goals"] = details[5]    # details[4] is partial url, detail[5] will be added in main function
        return match_complete_dict
  
    def leagues_and_matches_complete_details(self, details):
        '''
        Return match results and goals details for every leagues, in dictionary format.

        example of dictionary (JSON format) to return as leagues and matches details with goals.

        {
            "results": [
                {
                    "league": "England - Premier League",
                    "matches": [
                        {
                            "time": "21:00" / "88'" / "FT",
                            "home_team": "Juventus",
                            "away_team": "Fiorentina",
                            "result": "2 - 1",
                            "goals": [
                                {
                                    "goal_type": "goal" / "own-goal" / "pen-goal",
                                    "min": "13'",
                                    "partial_score": "1 - 0",
                                    "scorer_type": "home" / "away",
                                    "scorer_name": "Roberto Baggio"
                                },
                                {
                                    "goal_type": "goal" / "own-goal" / "pen-goal",
                                    "min": "26'",
                                    "partial_score": "1 - 1",
                                    "scorer_type": "home" / "away",
                                    "scorer_name": "Roberto Baggio"
                                },
                                {
                                    "goal_type": "goal" / "own-goal" / "pen-goal",
                                    "min": "88'",
                                    "partial_score": "2 - 1",
                                    "scorer_type": "home" / "away",
                                    "scorer_name": "Roberto Baggio"
                                }
                            ]
                        },
                        {
                            "time": "21:00" / "88'" / "FT",
                            "home_team": "Juventus",
                            "away_team": "Fiorentina",
                            "result": "2 - 1",
                            "goals": [
                                {
                                    "goal_type": "goal" / "own-goal" / "pen-goal",
                                    "min": "13'",
                                    "partial_score": "1 - 0",
                                    "scorer_type": "home" / "away",
                                    "scorer_name": "Roberto Baggio"
                                },
                                {
                                    "goal_type": "goal" / "own-goal" / "pen-goal",
                                    "min": "26'",
                                    "partial_score": "1 - 1",
                                    "scorer_type": "home" / "away",
                                    "scorer_name": "Roberto Baggio"
                                },
                                {
                                    "goal_type": "goal" / "own-goal" / "pen-goal",
                                    "min": "88'",
                                    "partial_score": "2 - 1",
                                    "scorer_type": "home" / "away",
                                    "scorer_name": "Roberto Baggio"
                                }
                            ]
                        }
                    ]
                },
                {
                    "league": "Italy - Serie A",
                    "matches": [
                        {
                            "time": "21:00" / "88'" / "FT",
                            "home_team": "Juventus",
                            "away_team": "Fiorentina",
                            "result": "2 - 1",
                            "goals": [
                                {
                                    "goal_type": "goal" / "own-goal" / "pen-goal",
                                    "min": "13'",
                                    "partial_score": "1 - 0",
                                    "scorer_type": "home" / "away",
                                    "scorer_name": "Roberto Baggio"
                                },
                                {
                                    "goal_type": "goal" / "own-goal" / "pen-goal",
                                    "min": "26'",
                                    "partial_score": "1 - 1",
                                    "scorer_type": "home" / "away",
                                    "scorer_name": "Roberto Baggio"
                                },
                                {
                                    "goal_type": "goal" / "own-goal" / "pen-goal",
                                    "min": "88'",
                                    "partial_score": "2 - 1",
                                    "scorer_type": "home" / "away",
                                    "scorer_name": "Roberto Baggio"
                                }
                            ]
                        },
                        {
                            "time": "21:00" / "88'" / "FT",
                            "home_team": "Juventus",
                            "away_team": "Fiorentina",
                            "result": "2 - 1",
                            "goals": [
                                {
                                    "goal_type": "goal" / "own-goal" / "pen-goal",
                                    "min": "13'",
                                    "partial_score": "1 - 0",
                                    "scorer_type": "home" / "away",
                                    "scorer_name": "Roberto Baggio"
                                },
                                {
                                    "goal_type": "goal" / "own-goal" / "pen-goal",
                                    "min": "26'",
                                    "partial_score": "1 - 1",
                                    "scorer_type": "home" / "away",
                                    "scorer_name": "Roberto Baggio"
                                },
                                {
                                    "goal_type": "goal" / "own-goal" / "pen-goal",
                                    "min": "88'",
                                    "partial_score": "2 - 1",
                                    "scorer_type": "home" / "away",
                                    "scorer_name": "Roberto Baggio"
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        :param details: list containing league, match details (each match is a dictionary) and goal details (each goal event is a dictionary) of every match.
        :returns: dictionary containing leagues and matches details with goals.
        '''
        leagues_and_matches_complete_dict = {}
        leagues_and_matches_complete_dict["results"] = details
        return leagues_and_matches_complete_dict

def main(mode="JSON"):
    '''
    Main routine execution
    
    :param mode: "text" or "JSON" are accepted. Default is "JSON". Optional.
    '''
    ls = LiveScore()
    homepage = ls.get_html()
    #homepage = ls.get_html("/soccer/2019-05-13/")    # to execute tests when there are no events today

    leagues = ls.leagues_finder(homepage)
    leagues_and_matches_details_list = []

    for league in leagues:
        league_title = league[0]    # league name - not used right now, will be used in leagues_and_matches_complete_details method
        league_matches_html_elements = ls.matches_finder(homepage, league[1])    # league's matchs html elements
        match_details_list = []
        for i in range(len(league_matches_html_elements)):
            match_details = ls.match_parser(league_matches_html_elements[i])    # maybe change var name since it's the same as a method (match_details)
            if mode == "text":
                print(ls.match_details(match_details))    # print match details json format test
            elif mode == "JSON":
                print(json.dumps(ls.match_details(match_details), indent=4))    # print match details json format test (pretty print)
            match_page = ls.get_html(ls.match_parser(league_matches_html_elements[i])[4])    # get html passing match partial url as argument ([4])
            goal_details_list = []
            for incident in ls.event_finder(match_page):
                if ls.goal_finder(incident) is not None:    # to exclude None object coming from goal_finder (implicit else)
                    # TODO: add management of explicit else statement (if ls.goal_finder(incident) is not "other-event")
                    goal_details = ls.goal_parser(ls.goal_finder(incident)[0], ls.goal_finder(incident)[1])    # list containing goal details [goal type, details]
                    if mode == "text":
                        print(ls.goal_details(goal_details))    # print goal details json format test
                    elif mode == "JSON":
                        print(json.dumps(ls.goal_details(goal_details), indent=4))    # print goal details json format test (pretty print)
                    goal_details_list.append(ls.goal_details(goal_details))
            match_details.append(goal_details_list)
            if mode == "text":
                print(ls.match_complete_details(match_details))    # OK - print match complete details json format test
            elif mode == "JSON":
                print(json.dumps(ls.match_complete_details(match_details), indent=4))    # OK - print match complete details json format test (pretty print)
            match_details_list.append(ls.match_complete_details(match_details))
        leagues_and_matches_details_dict = {}
        leagues_and_matches_details_dict["league"] = league_title
        leagues_and_matches_details_dict["matches"] = match_details_list
        leagues_and_matches_details_list.append(leagues_and_matches_details_dict)
    if mode == "text":
        print(ls.leagues_and_matches_complete_details(leagues_and_matches_details_list))    # OK - print leagues and matches complete details json test - complete dictionary
    elif mode == "JSON":
        print(json.dumps(ls.leagues_and_matches_complete_details(leagues_and_matches_details_list), indent=4))    # OK - print leagues and matches complete details json test - complete dictionary (pretty print)
    # TODO: try to find a way to construct the complete dictionary all inside leagues_and_matches_complete_details method
    # TODO: maybe creating another method to construct temporary dict?
    # TODO: evaluate if main function should became a method of class LiveScore
    # TODO: if it's possible, inside each method, add mid-steps executed to return JSON format, so main function will be very short and basic

if __name__ == "__main__":
    main()