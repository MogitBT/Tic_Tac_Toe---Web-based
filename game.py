import random

class Game:
    structure = ["_" for _ in range(9)]
    current_player = 'X'
    tutorial_step = 0
    hint_index = 0
    tutorial_count = 0
    combination = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    bot_combination = [
        [6, 4, 8], [1, 8, 6], [0, 4, 2],
        [2, 4, 8], [0, 2, 8], [0, 4, 6],
        [1, 6, 4], [1, 3, 7]
    ]

    def layout():
        return [Game.structure[i:i+3] for i in range(0, 9, 3)]

    def user_input(position, player):
        if position.isdigit() and int(position) in range(1, 10):
            if Game.structure[int(position) - 1] == "_":
                Game.structure[int(position) - 1] = player
                return True
            else:
                return False
        return False

    def check(player):
        for possibility in Game.combination:
            if all(Game.structure[i] == player for i in possibility):
                return True
        return False

    def draw():
        if "_" not in Game.structure:
            return True
        return False

    def refresh():
        Game.structure = ["_" for _ in range(9)]
        Game.current_player = 'X'
        Game.tutorial_step = 0
        Game.hint_index = 0
        Game.tutorial_count = 0

    def update(position, player):
        if Game.user_input(position, player):
            if Game.check(player):
                return f'Player {player} won!'
            elif Game.draw():
                return 'Match Draw!'
            else:
                Game.current_player = 'O' if player == 'X' else 'X'
                return ''
        else:
            return 'Invalid move'

    def bot_move_logic():
        combinations = Game.combination
        position = -1

        for combination in combinations:
            bot_count = 0
            empty_spot = -1
            for i in combination:
                if Game.structure[i] == 'O':
                    bot_count += 1
                elif Game.structure[i] == '_':
                    empty_spot = i
            if bot_count == 2 and empty_spot != -1:
                position = empty_spot
                break

        if position == -1:
            for combination in combinations:
                player_count = 0
                empty_spot = -1
                for i in combination:
                    if Game.structure[i] == 'X':
                        player_count += 1
                    elif Game.structure[i] == '_':
                        empty_spot = i
                if player_count == 2 and empty_spot != -1:
                    position = empty_spot
                    break

        if position == -1 and Game.structure[4] == '_':
            position = 4

        if position == -1:
            empty_positions = [i for i in range(9) if Game.structure[i] == '_']
            if empty_positions:
                position = random.choice(empty_positions)

        position = str(position + 1)
        message = Game.update(position, 'O')

        return int(position) - 1, message  # Return the position and the message

    def tutorial_logic():
        if Game.tutorial_step < len(Game.combination):
            next_hint_position = Game.combination[Game.tutorial_count][Game.hint_index]
            if Game.structure[next_hint_position] == "_":
                Game.structure[next_hint_position] = "√"
        else:
            Game.refresh()

    def tutorial_update(position):
        if position.isdigit() and int(position) in range(1, 10):
            pos_index = int(position) - 1
            if Game.tutorial_step < len(Game.combination):
                expected_positions = Game.combination[Game.tutorial_step]
                if pos_index == expected_positions[Game.hint_index]:
                    Game.structure[pos_index] = "X"
                    Game.hint_index += 1
                    if Game.hint_index == len(expected_positions):
                        Game.tutorial_step += 1
                        Game.hint_index = 0
                        Game.tutorial_count += 1
                        if Game.tutorial_step < len(Game.combination):
                            Game.structure = ["_" for _ in range(9)]
                            Game.tutorial_logic()
                            return "Well done! Proceeded to the next level."
                        else:
                            Game.refresh()
                            return "Tutorial complete! You've learned all the steps."
                    else:
                        bot_positions = Game.bot_combination[Game.tutorial_step]
                        for bot_pos in bot_positions:
                            if Game.structure[bot_pos] == '_':
                                Game.structure[bot_pos] = "O"
                                break
                        Game.tutorial_logic()
                        return "Correct move! Now it's your turn again."
                else:
                    return "Incorrect position. Try again."
            else:
                Game.refresh()
                return "Tutorial complete! You've learned all the steps."
        else:
            return "Invalid input. Please enter a number between 1 and 9."
        
       
