from colorfight import Colorfight
import time
import random
from colorfight.constants import BLD_GOLD_MINE, BLD_ENERGY_WELL, BLD_FORTRESS, BUILDING_COST
def main():
	game = Colorfight()
	play_game(game)


def play_game(
        game, \
        room     = 'DeepMines', \
        username = 'DeepMine-v0.1', \
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

            # calculate number of buildings and cells we have
            buildings = 0
            cells = len(game.me.cells.values())
            for cell in game.me.cells.values():
            	if cell.building.name != 'empty':
            		buildings += 1

            # Check if you exist in the game. If not, wait for the next round.
            # You may not appear immediately after you join. But you should be 
            # in the game after one round.
            if game.me == None:
                continue
    
            me = game.me
            # print(upgrade_val(game, game.game_map[(5, 5)], 1, 1, buildings))
            ### unknown
            
            # Send the command list to the server
            result = game.send_cmd(cmd_list)
            print(result)

    # Do this to release all the allocated resources. 
    game.disconnect()

def expansion(game, cell, gold_coefficient, energy_coefficient, ncost_coefficient, sum1_coefficient, sum2_coefficient, expansion_coefficient, distance = 0):
    map = game.game_map
    gold_value = cell.natural_gold*gold_coefficient
    energy_value = cell.natural_energy*energy_coefficient
    ncost_value = cell.attack_cost*ncost_coefficient
    sum1_total = 0
    sum2_total = 0
    if distance < 2:
        position = cell.position
        surrounding = position.get_surrounding_cardinals()
        for adjacent in surrounding:
            if adjacent.is_valid():
                sum1_total+=expansion(game, cell, gold_coefficient, energy_coefficient, ncost_coefficient, sum1_coefficient, sum2_coefficient, expansion_coefficient, distance+1)
        if distance == 0:
            surrounding = position.get_surrounding_cardinals()
            for adjacent in surrounding:
                if adjacent.is_valid():
                    sum1_total+=expansion(game, cell, gold_coefficient, energy_coefficient, ncost_coefficient, sum1_coefficient, sum2_coefficient, expansion_coefficient, distance+2)
    return (gold_value+energy_value-ncost_value+sum1_total*sum1_coefficient+sum2_total*sum2_coefficient)*expansion_coefficient
def defense():
	pass
def build():
	pass

# calculates the upgrade value for a cell
# val = net change in gold rate * gold_co + net change in energy rate * energy_co
# returns 0 if no building or can't be upgraded
def upgrade_val(game, cell, energy_co, gold_co):
	# if there is no building, or it can't be upgraded, return 0
	if cell.building.name == 'empty' or cell.building.level == cell.building.max_level \
		or cell.building.level == cell.building.tech_level:

		return 0
	# else, building can be upgraded
	else:
		if cell.building.name == "energy_well":
			return energy_co * natural_energy
		elif cell.building.name == 'gold_mine':
			return gold_co * natural_gold
		else: 
			return 0

if __name__ == '__main__':
	main()
