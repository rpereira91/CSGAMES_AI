from src.bot.Bot import Bot
from src.symbols.ObjectSymbols import ObjectSymbols
import copy
import time
import math

# TODO:
# - Make a list of possible moves to get to a resource (first 5 maybe?)


class SmartBot(Bot):
    def __init__(self):
        super().__init__()
        self.find_resource = True

        

    def get_name(self):
        return 'SmartBot'

    def turn(self, game_state, character_state, other_bots):
        super().turn(game_state, character_state, other_bots)
        # print(self.character_state)
        # return self.commands.idle()
        # return self.search_for_resource(game_state, other_bots)
        """
        if not carrying:
            find and go to resource
        if carrying and on resource and sufficient health and no nearby bot
            keep collecting
        if carrying and on resource and sufficient health and one nearby bot
            if can win
                attack
            else
                leave
        if carrying and on resource and sufficient health and multiple nearby bots
            leave
        if carrying and on resource and insufficient health
            (try to) return to base
        if carrying and not on resource
            return to base
        if on base and carrying
            deposit
        if on base and not carrying and insufficient health
            heal
        """
        game_state_array = [list(state) for state in copy.deepcopy(game_state).split('\n')]
        # Carrying and on base => store
        if int(character_state['carrying']) > 0 and character_state['location'] == character_state['base']:
            return self.commands.store()
        # On base and needs health => rest
        if character_state['location'] == character_state['base'] and int(character_state['health']) < 100:
            return self.commands.rest()
        # Carrying and not on resource (Must be running) => return to base
        if int(character_state['carrying']) > 0 and game_state_array[int(character_state['location'][0])][int(character_state['location'][1])] != 'J':
            return self.move_towards_base(game_state_array)
        # On resource
        if game_state_array[int(character_state['location'][0])][int(character_state['location'][1])] == 'J':
            # Low health => return to base
            bots = self.get_nearby_bots(other_bots)
            num_bots = len(bots)
            # No bots nearby => collect
            if num_bots == 0 and int(character_state['health']) <= 30:
                return self.move_towards_base(game_state_array)
            if num_bots == 0:
                return self.commands.collect()
            # One bot nearby => Decide if we can win
            if num_bots == 1:
                bot = bots[0]
                my_hits_to_death = math.ceil(int(self.character_state['health']))
                bot_hits_to_death = math.ceil(int(bot['health']))
                # If we can't win the fight => Run to base
                if my_hits_to_death < bot_hits_to_death:
                    return self.move_towards_base(game_state_array)
                # Can win the fight
                else:
                    return self.attack_bot(bot)
                pass
            if num_bots > 1 and int(character_state['health']) > 60:
                return self.commands.collect()
            if num_bots > 1:
                return self.move_towards_base(game_state_array)

        # Otherwise, move towards resource
        return self.get_move_towards_resource(game_state_array, other_bots)

    def attack_bot(self, bot):
        my_x, my_y = self.character_state['location']
        bot_x, bot_y = bot['location']
        if bot_x < my_x:
            return self.commands.attack('N')
        elif bot_x > my_x:
            return self.commands.attack('S')
        elif bot_y < my_y:
            return self.commands.attack('W')
        elif bot_y > my_y:
            return self.commands.attack('E')
        
    def get_nearby_bots(self, other_bots):
        loc = self.character_state['location']
        my_x, my_y = loc
        bot_count = 0
        bots = []
        for bot in other_bots:
            bot_loc = other_bots['location']
            bot_x, bot_y = bot_loc
            if abs(bot_x-my_x) + abs(bot_y - my_y) == 1:
                bot_count += 1
                bots.append(bot)
        return bots

    def get_move_towards_resource(self, game_state_array, other_bots, excluded_resources = []):
        top_paths = self.get_top_5_paths(game_state_array, other_bots, excluded_resources)
        if len(top_paths) == 0:
            return self.commands.idle()
        best_move = None
        best_move_val = 100000000
        for path in top_paths:
            loc, move_list, damage = path
            if len(move_list) == 0:
                continue
            moves_to_heal = math.ceil(damage/10)
            move_val = len(move_list) + moves_to_heal
            if move_val < best_move_val:
                best_move = move_list
                best_move_val = move_val
        if best_move == None:
            return self.commands.idle()
        # Check for bots if we are close to resource
        bots = self.get_nearby_bots(other_bots)
        if len(best_move) == 1 and len(bots) >= 1:
            my_x, my_y = self.character_state['location']
            for bot in bots:
                bot_x, bot_y = bot['location']
                my_hits_to_death = math.ceil(int(self.character_state['health']))
                bot_hits_to_death = math.ceil(int(bot['health']))
                if bot_x < my_x and best_move[0] == 'N':
                    if my_hits_to_death < bot_hits_to_death:
                        excluded_resources.append((bot_x, bot_y))
                        return self.get_move_towards_resource(game_state_array, other_bots, excluded_resources)
                    else:
                        return self.commands.attack('N')
                elif bot_x > my_x and best_move[0] == 'S':
                    if my_hits_to_death < bot_hits_to_death:
                        excluded_resources.append((bot_x, bot_y))
                        return self.get_move_towards_resource(game_state_array, other_bots, excluded_resources)
                    else:
                        return self.commands.attack('S')
                elif bot_y < my_y and best_move[0] == 'W':
                    if my_hits_to_death < bot_hits_to_death:
                        excluded_resources.append((bot_x, bot_y))
                        return self.get_move_towards_resource(game_state_array, other_bots, excluded_resources)
                    else:
                        return self.commands.attack('W')
                elif bot_y > my_y and best_move[0] == 'E':
                    if my_hits_to_death < bot_hits_to_death:
                        excluded_resources.append((bot_x, bot_y))
                        return self.get_move_towards_resource(game_state_array, other_bots, excluded_resources)
                    else:
                        return self.commands.attack('E')
        return self.commands.move(best_move[0])

    def move_towards_base(game_state_arrayself, game_state_array):
        queue = []
        queue.append(((self.character_state['location']), '', 0))
        while(len(queue) > 0):
            loc, move_list, damage = queue.pop()
            x,y = loc
            # Found a resource, break
            if loc == self.character_state['base']:
                break
            # Ignore a spot we have already been on
            if game_state_array[x][y] == '.':
                continue
            # Ignore empty bases
            if game_state_array[x][y] == 'B':
                continue
            # Can't go on trees or water
            if game_state_array[x][y] == '1':
                continue
            if game_state_array[x][y] == '2':
                continue
            # Check for bots and bot bases
            do_continue = False
            for bot in other_bots:
                # Can't move onto bot
                if x == bot['location'][0] and y == bot['location'][1]:
                    do_continue = True
                    break
                # Can't move onto other base
                if x == bot['base'][0] and y == bot['base'][1]:
                    do_continue = True
                    break
            if do_continue:
                continue
            # Can take _some_ damage
            if game_state_array[x][y] == 'S':
                damage += 12 # Upper end of average amount
                # If we would be too low to take 3 hits from enemy bots, then don't do the move
                if int(self.character_state['health']) - damage <= 30: 
                    continue

            # It is a valid move, so add other moves
            game_state_array[x][y] = '.'
            queue.insert(0, ((x,y+1), move_list+'E', damage))
            queue.insert(0, ((x,y-1), move_list+'W', damage))
            queue.insert(0, ((x-1,y), move_list+'N', damage))
            queue.insert(0, ((x+1,y), move_list+'S', damage))
        if len(self.move_list) == 0:
            return self.commands.idle()
        return self.commands.move(move_list[0])

    def get_top_5_paths(self, game_state_array, other_bots, excluded_resources):
        queue = []
        queue.append(((self.character_state['location']), '', 0))
        resulting_paths = []
        while(len(queue) > 0):
            loc, move_list, damage = queue.pop()
            x,y = loc
            # Found a resource, break
            if game_state_array[x][y] == 'J':
                if (x,y) not in excluded_resources:
                    resulting_paths.append((loc, move_list, damage))
                    if len(resulting_paths) >= 5:
                        break
                else:
                    continue
            # Ignore a spot we have already been on
            if game_state_array[x][y] == '.':
                continue
            # Ignore empty bases
            if game_state_array[x][y] == 'B':
                continue
            # Can't go on trees or water
            if game_state_array[x][y] == '1':
                continue
            if game_state_array[x][y] == '2':
                continue
            # Check for bots and bot bases
            do_continue = False
            for bot in other_bots:
                # Can't move onto bot
                if x == bot['location'][0] and y == bot['location'][1]:
                    do_continue = True
                    break
                # Can't move onto other base
                if x == bot['base'][0] and y == bot['base'][1]:
                    do_continue = True
                    break
            if do_continue:
                continue
            # Can take _some_ damage
            if game_state_array[x][y] == 'S':
                damage += 12 # Upper end of average amount
                # If we would be too low to take 3 hits from enemy bots, then don't do the move
                if int(self.character_state['health']) - damage <= 30: 
                    continue

            # It is a valid move, so add other moves
            game_state_array[x][y] = '.'
            queue.insert(0, ((x,y+1), move_list+'E', damage))
            queue.insert(0, ((x,y-1), move_list+'W', damage))
            queue.insert(0, ((x-1,y), move_list+'N', damage))
            queue.insert(0, ((x+1,y), move_list+'S', damage))
        return resulting_paths
