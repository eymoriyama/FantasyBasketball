

class Player():
    def __init__(self, position, name, salary, pfp, value):
        self.self = self
        self.name = name
        self.salary = salary
        self.pfp = pfp
        self.value = value
        self.position = position
        self.diff = 100
        self.position_out = None
        self.third_position = 'u'
        if position == 'pg' or position == 'sg':
            self.second_position = 'g'
        elif position == 'sf' or position == 'pf':
            self.second_position = 'f'
        else:
            self.second_position = 'c'
        
    def __iter__(self):
        return iter(self.list)
    
    def __str__(self):
        return "{} {} {} {}".format(self.name,self.position,self.second_position,self.salary, self.pfp)


class Team():
    def __init__(self, team_dic):
        self.team_dic = team_dic
        self.positions =list(team_dic.keys())
        self.players_list = list(team_dic.values())
        self.players = self.getPlayers()
        self.points = self.getTotalPoints()
        self.budget = self.getBudget()
        self.under_budget = self.underBudget()

    def getTotalPoints(self):
        total_points = 0
        for player in self.players_list:
            total_points += player.pfp
        return total_points

    def getBudget(self):
        budget = 0
        for player in self.players_list:
            budget += player.salary
        return budget

    def getPlayers(self):
        players = tuple()
        for player in self.players_list:
            players = players + (player.name,)
        return players

    def underBudget(self):
        budget = 0
        for player in self.players_list:
            budget += player.salary
        if budget <= 50000:
            return True
        else:
            return False

  





