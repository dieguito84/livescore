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