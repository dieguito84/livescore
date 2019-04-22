class LiveScore():
    
    def get_html(self, url, user_agent):
        '''
        Returns HTML page as <class 'requests_html.HTML'> object

        Gets HTML page and renders it using requests-html library
        It supports JavaScript 
        '''
        _session = HTMLSession()
        _page = _session.get(url, headers={"User-Agent": user_agent})
        _page.html.render()
        return _page.html

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