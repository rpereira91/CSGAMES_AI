from src.bot.Bot import Bot
from src.symbols.ObjectSymbols import ObjectSymbols
import copy
import time

class PeacefulBot(Bot):
    def __init__(self):
        super().__init__()
        self.turns_mining = 0
        

    def get_name(self):
        return 'AgroBot'

    def turn(self, game_state, character_state, other_bots):
        super().turn(game_state, character_state, other_bots)
        # print(self.character_state)
        # return self.commands.idle()
        return self.search_for_resource(game_state, other_bots)

    def search_for_resource(self, game_state, other_bots):
        # If hurt, go to base
        if self.turns_mining > 5:
            goal = self.character_state['base']
            direction = self.pathfinder.get_next_direction(self.character_state['location'], goal)
            if direction:
                return self.commands.move(direction)
            else:
                self.turns_mining = 0
                return self.commands.store()
        if int(self.character_state['health']) < 100:
            goal = self.character_state['base']
            direction = self.pathfinder.get_next_direction(self.character_state['location'], goal)
            if direction:
                return self.commands.move(direction)
            else:
                return self.commands.rest()
        copy_game_state = copy.deepcopy(game_state).split('\n')
        copy_game_state = [list(state) for state in copy_game_state]

        copy_game_state = [list(state) for state in copy.deepcopy(game_state).split('\n')]
        queue = []
        queue.append(((self.character_state['location']), ''))
        while(True):
            loc, move = queue.pop()
            x,y = loc
            # Found a resource, break
            if copy_game_state[x][y] == 'J':
                break
            # Ignore spots we've been on
            elif copy_game_state[x][y] == '.':
                continue
            # Can't go on bad spots
            elif copy_game_state[x][y] == '1':
                continue
            elif copy_game_state[x][y] == '2':
                continue
            # Ignore danger spots (for now)
            elif copy_game_state[x][y] == 'S':
                continue
            # Check for bots
            for bot in other_bots:
                # Same location as bot
                if x == bot['location'][0] and y == bot['location'][1]:
                    break
                # On the other bots base
                elif x == bot['base'][0] and y == bot['base'][1]:
                    break
            # Now this is a valid move to make
            copy_game_state[x][y] = '.'
            # Add next moves
            # if len(move) == 1:
            #     queue.insert(0, ((x-1, y), move)) # Left 
            #     queue.insert(0, ((x+1, y), move)) # Right
            #     queue.insert(0, ((x, y-1), move)) # Up
            #     queue.insert(0, ((x, y+1), move)) # Down
            # else:
            queue.insert(0,((x, y+1), move+'E')) # Left 
            queue.insert(0,((x, y-1), move+'W')) # Right
            queue.insert(0,((x-1, y), move+'N')) # Up
            queue.insert(0,((x+1, y), move+'S')) # Down
                
        if len(move) == 0: # On resource
            self.turns_mining += 1
            return self.commands.collect()
        else: # Not on resource
            return self.commands.move(move[0])