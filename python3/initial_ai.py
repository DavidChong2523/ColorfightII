from colorfight import Colorfight
import time
import random
import math
from colorfight.constants import BLD_GOLD_MINE, BLD_ENERGY_WELL, BLD_FORTRESS, BUILDING_COST
def main():
    game = Colorfight()
    play_game(game)

def play_game(
        game, \
        room     = 'DeepMines', \
        username = 'DeepMine-v0.3', \
        password = 'uclaacm', \
        join_key = '12508'):
    # Connect to the server. This will connect to the public room. If you want to
    # join other rooms, you need to change the argument
    game.connect(room = room)

    # game.register should return True if succeed.
    # As no duplicate usernames are allowed, a random integer string is appended
    # to the example username. You don't need to do this, change the username
    # to your ID.
    # You need to set a password. For the example AI, the current time is used
    # as the password. You should change it to something that will not change 
    # between runs so you can continue the game if disconnected.
    if game.register(username = username, \
            password = password, join_key = join_key):

        # This is the game loop
        while True:

            #########COEFFECIENTS#########
            THREAT_SPENDING_CONSTANT = 0.5
            energy_co, gold_co = calc_coefficients(game)
            threat_coeffecient = 1
            expansion_coefficient = 1
            
            # The command list we will send to the server
            cmd_list = []

            # The list of cells that we want to attack
            my_attack_list = []
            # update_turn() is required to get the latest information from the
            # server. This will halt the program until it receives the updated
            # information. 
            # After update_turn(), game object will be updated.   
            # update_turn() returns a Boolean value indicating if it's still 
            # the same game. If it's not, break out
            if not game.update_turn():
                break

            # Check if you exist in the game. If not, wait for the next round.
            # You may not appear immediately after you join. But you should be 
            # in the game after one round.
            if game.me == None:
                continue
    
            me = game.me
            game_map = game.game_map
        
            # calculate number of buildings we have
            buildings = 0
            for cell in game.me.cells.values():
                if cell.building.name != 'empty':
                    buildings += 1


            # expand
            # first val is result, second is position tuple
            expansion_list = []
            for cell in game.me.cells.values():
                surrounding = cell.position.get_surrounding_cardinals()
                for adjacent in surrounding:
                    if game.game_map[adjacent].owner is not game.me.uid and game.game_map[adjacent].position.is_valid():
                        expansion_list.append((expansion(game, game.game_map[adjacent]), adjacent))
            '''
            for key in sorted(expansion_list, key=lambda expansion: expansion[0], reverse=True):
                if game.me.energy > game.game_map[key[1]].attack_cost:
                    cmd_list.append(game.attack(key[1], game.game_map[key[1]].attack_cost))
                    game.me.energy -= game.game_map[key[1]].attack_cost
                else:
                    break
            '''
            # finds threat values of all values on the edge of our fort
            edge_cells = []
            for cell in game.me.cells.values():
                surrounding = cell.position.get_surrounding_cardinals()
                on_edge = False
                for pos in surrounding:
                    if game.game_map[pos].owner is not game.me.uid:
                        on_edge = True
                        break
                if on_edge:
                    edge_cells.append(cell)

            threat_list = []
            for cell in edge_cells:
                threat_val = threat(game, cell, gold_co, energy_co, threat_coeffecient)
                threat_list.append((threat_val, cell.position))

            build_list = []
            for cell in game.me.cells.values():
                build_list.append((build(game, cell, energy_co, gold_co), cell.position))
            upgrade_list = []
            defense_list = []
            for cell in game.me.cells.values():
                upgrade_list.append((upgrade_val(game, cell, energy_co, gold_co), cell.position))
                defense_list.append((defense(game, cell, energy_co, gold_co), cell.position))
		    
            
            # master lists for commands
            GOLD_MASTER_LIST = []
            
            GOLD_MASTER_LIST = build_list+upgrade_list
            for key in sorted(GOLD_MASTER_LIST, key=lambda gold: gold[0], reverse=True):
                if game.game_map[key[1]].is_empty:
                    if not game.turn > 450:
                        cmd_list.append(game.build(game.game_map[key[1]].position, best_build(game, cell, energy_co, gold_co)))
                elif game.game_map[key[1]].building.can_upgrade :
                    if game.game_map[key[1]].building.upgrade_gold < game.me.gold :
                        if not game.turn > 450:
                            cmd_list.append(game.upgrade(game.game_map[key[1]].position))
                        game.me.gold -= game.game_map[key[1]].building.upgrade_gold

            # Combine the two lists
            ENERGY_MASTER_LIST = defense_list+expansion_list
            
            for key in sorted(ENERGY_MASTER_LIST, key=lambda energy: energy[0], reverse=True):
                '''if game.game_map[key[1]].owner is game.me.uid and game.me.energy > key[0]*THREAT_SPENDING_CONSTANT:
                    cmd_list.append(game.attack(key[1], key[0]*THREAT_SPENDING_CONSTANT))'''
                built_fortress = False
                if game.game_map[key[1]].owner is game.me.uid:
                    adjacent = game.game_map[key[1]].position.get_surrounding_cardinals()
                    for test_cell in adjacent:
                        if(game_map[test_cell].owner != me.uid and game_map[test_cell].owner != 0):
                            cmd_list.append(game.build(game.game_map[key[1]].position, BLD_FORTRESS))
                            built_fortress = True
                            break
                if(not built_fortress and game.me.energy > game.game_map[key[1]].attack_cost):
                    cmd_list.append(game.attack(key[1], game.game_map[key[1]].attack_cost))
            """while game.me.energy > 0:
                print(threat_list)
                print(expansion_list)
                if len(expansion_list) == 0 or threat_list[0][0] >= expansion_list[0][0] :
                    # attack own cell
                    cmd_list.append(game.attack(threat_list[0][1], threat_list[0][0] * THREAT_SPENDING_CONSTANT))
                    threat_list = threat_list[1:]
                else:
                    # expand
                    cmd_list.append(game.attack(expansion_list[0][1], game.game_map[expansion_list[0][1]].attack_cost))
                    expansion_list = expansion_list[1:]"""

            # Send the command list to the server
            result = game.send_cmd(cmd_list)
            print(result)

    # Do this to release all the allocated resources. 
    game.disconnect()

def calc_coefficients(game):
    HALF_TURNS = 250
    turn = game.turn

    gold_co = turn / HALF_TURNS + 1
    energy_co = 1 - (turn / HALF_TURNS)
    if(turn > HALF_TURNS):
        gold_co = 1
        energy_co = 0
    
    gold_co += 1
    energy_co += 1
    return energy_co, gold_co
    

def expansion(game, cell, gold_coefficient = 1, energy_coefficient = 1, ncost_coefficient = 0.0025, sum1_coefficient = 0.1, sum2_coefficient = 0.01, expansion_coefficient = 1, distance = 0):
    if cell.is_home:
        return 1000
    map = game.game_map
    gold_value = cell.natural_gold * gold_coefficient
    energy_value = cell.natural_energy * energy_coefficient
    ncost_value = cell.attack_cost*ncost_coefficient
    sum1_total = 0
    sum2_total = 0
    if distance < 2:
        position = cell.position
        surrounding = position.get_surrounding_cardinals()
        for adjacent in surrounding:
            if adjacent.is_valid() and map[adjacent].owner is not game.me.uid:
                sum1_total+=expansion(game, cell, gold_coefficient, energy_coefficient, ncost_coefficient, sum1_coefficient, sum2_coefficient, expansion_coefficient, distance+1)
        if distance == 0:
            surrounding = position.get_surrounding_cardinals()
            for adjacent in surrounding:
                if adjacent.is_valid() and map[adjacent].owner is not game.me.uid:
                    sum1_total+=expansion(game, cell, gold_coefficient, energy_coefficient, ncost_coefficient, sum1_coefficient, sum2_coefficient, expansion_coefficient, distance+2)
    home = 0
    homePos = 0
    for myCell in game.me.cells.values():
        if myCell.is_home:
            homePos = myCell.position
    if homePos is not 0:
        home = ((homePos.x-cell.position.x)**2+(homePos.y-cell.position.y)**2)**0.5

    val = ((gold_value+energy_value)/ncost_value+sum1_total*sum1_coefficient+sum2_total*sum2_coefficient)*expansion_coefficient-home
    print("expansion:", val)
    return val

def defense(game, cell, energy_co, gold_co):
    game_map = game.game_map
    me = game.me

    value = 0
    cell_val = general_val(game, cell, energy_co, gold_co)
    position = cell.position
    x = position.x
    y = position.y
    
    # check for enemy cells in 7x7 centered on cell
    MAX_STEPS_TO_ATTACK = 4
    for testX in range(x-2, x+3):
        for testY in range(y-2, y+3):
            if(testX < game_map.width and testX >= 0 and \
               testY < game_map.height and testY >= 0):
                testCell = game_map[(testX, testY)]
            else:
                continue
  
            # own cell
            if(testCell.owner == me.uid):
                continue
            # empty cell
            elif(testCell.owner == 0):
                continue
            # opponent cell
            else:
                print("oppoenent near")
                dist = testCell.position - position
                steps_to_attack = abs(dist.x) + abs(dist.y)
                test_value = MAX_STEPS_TO_ATTACK / steps_to_attack
                if(test_value > value):
                    value = test_value
    value /= 6
    value *= cell_val
    print("fortress val", value)
    return value

# how threatened cells are from enemy attacks
def threat(game, cell, energy_co = 1, gold_co = 1, threat_co=1):
    game_map = game.game_map
    me = game.me

    cell_value = general_val(game, cell, energy_co, gold_co)
    value = 0
    position = cell.position
    x = position.x
    y = position.y

    # check for enemy cells in 5x5 centered on cell
    MAX_STEPS_TO_ATTACK = 4
    for testX in range(x-2, x+3):
        for testY in range(y-2, y+3):
            if(testX < game_map.width and testX >= 0 and \
               testY < game_map.height and testY >= 0):
                testCell = game_map[(testX, testY)]
            else:
                continue
              
            # own cell
            if(testCell.owner == me.uid):
                continue
                        # empty cell
            elif(testCell.owner == 0):
                continue
                        # opponent cell
            else:
                dist = testCell.position - position
                steps_to_attack = abs(dist.x) + abs(dist.y)
                test_value = (MAX_STEPS_TO_ATTACK / steps_to_attack)
                if(test_value > value):
                    value = test_value
    value = value * cell_value
    return value
    

# returns best building option for the cell in the form of the build character
def best_build(game, cell, energy_co, gold_co):
    # return 0 if the cell isn't empty
    if cell.building.name != 'empty':
        return 0
    else:
        # return the better option of the two
        energy_well_val = cell.natural_energy * 2
        gold_mine_val = cell.natural_gold * 2
        if energy_well_val > gold_mine_val:
            return BLD_ENERGY_WELL
        else:
            return BLD_GOLD_MINE

# returns the value of building in a given cell
def build(game, cell, energy_co, gold_co):
    # if there is a building in the cell, do nothing
    if cell.building.name != 'empty':
        return 0
    else:
        # two options are well or mine, and return the greatest
        energy_well_val = cell.natural_energy * 2
        gold_mine_val = cell.natural_gold * 2
        return max(energy_well_val, gold_mine_val)


# calculates the upgrade value for a cell
# val = net change in gold rate * gold_co + net change in energy rate * energy_co
# returns 0 if no building or can't be upgraded
def upgrade_val(game, cell, energy_co, gold_co):
    # if there is no building, or it can't be upgraded, return 0
    if(cell.building.name == 'empty' or cell.building.level == cell.building.max_level \
        or (cell.building.level == game.me.tech_level and not cell.is_home)):
        return 0
    # else, building can be upgraded
    else:
        if(cell.building.name == "energy_well"):
            return energy_co * cell.natural_energy
        elif(cell.building.name == 'gold_mine'):
            return gold_co * cell.natural_gold
        else: 
            return 0
def general_val(game, cell, energy_co, gold_co):
    return cell.gold * gold_co + cell.energy * energy_co

if __name__ == '__main__':
    main()
