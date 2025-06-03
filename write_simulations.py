import random
import tkinter as tk
import copy
import csv

class GameState:
    def __init__(self):
        self.bomb = False
        self.quads = False
        self.player_turn = 0
        self.orig_piles = [[], [], [], []]
        self.pair_mode = False  # Track if we're in pairs mode
        self.triple_mode = False  # Track if we're in triples mode
        self.same_card_counter = False
        self.display_mode = False
        self.Final_Card = Card(1, 'clear')
        self.recently_played = []  # List to track recently played cards
        
    def copy_piles(self, pile1, pile2, pile3, pile4):
        self.orig_piles = [
            copy.deepcopy(pile1),
            copy.deepcopy(pile2),
            copy.deepcopy(pile3),
            copy.deepcopy(pile4)
        ]
    
    def get_orig_pile(self, player_idx):
        return self.orig_piles[player_idx]

    def reset_modes(self):
        self.pair_mode = False
        self.triple_mode = False
        
    def add_recently_played(self, card):
        self.recently_played.append(card)
        
    def clear_recently_played(self):
        self.recently_played = []

class Card:
    def __init__(self, value, color):
        self.value = value
        self.color = color

    def __str__(self):
        copy_card = copy.deepcopy(self)
        if self.value == 11:
            copy_card.value = 'J'
        if self.value == 12:
            copy_card.value = 'Q'
        if self.value == 13:
            copy_card.value = 'K'
        if self.value == 14:
            copy_card.value = 'A'
        return f"[{copy_card.value} of {self.color}]"

def create_cards():
    colors = ['hearts', 'diamonds', 'spades', 'clubs']
    deck = [Card(value, color) for value in range(2, 15) for color in colors]
    in_order = deck
    random.shuffle(deck)
    return deck


def split_deck(deck):
    pile1 = deck[:13]
    pile2 = deck[13:26]
    pile3 = deck[26:39]
    pile4 = deck[39:]
    return pile1, pile2, pile3, pile4


def choose_deck(pile1, pile2, pile3, pile4):
    topcard1 = pile1[0]
    topcard2 = pile2[0]
    topcard3 = pile3[0]
    topcard4 = pile4[0]

    choices = [topcard1.value, topcard2.value, topcard3.value, topcard4.value]
    choice = choices[0]
    index = 0
    for i in range(4):
        if choices[i] > choice:
            choice = choices[i]
            index = i
        if choices[i] == 2:
            index = i
            break

    if index == 0: return pile1, pile2, pile3, pile4
    elif index == 1: return pile2, pile1, pile3, pile4
    elif index == 2: return pile3, pile1, pile2, pile4
    else: return pile4, pile1, pile2, pile3


def swap_cards(winners_pile, losers_pile):
    non_twos = [c for c in winners_pile if c.value != 2]
    worst_card = min(non_twos, key=lambda c: c.value)

    # 2) Winner takes the best card from the loser (2's are highest):
    best_card = max(losers_pile, key=lambda c: (c.value == 2, c.value))

    # 3) Perform the swap in each hand
    wi = winners_pile.index(worst_card)
    li = losers_pile.index(best_card)
    winners_pile[wi], losers_pile[li] = losers_pile[li], winners_pile[wi]


def organize_cards(pile):
    pile.sort(key=lambda card: card.value)
    return pile


def quads(game_state, prev_card, pile):
    if len(pile) <= 3: return prev_card, pile
    
    for i in range(len(pile) - 3):
        if pile[i].value != 2:
            if (pile[i].value == pile[i+3].value):
                if game_state.display_mode: print(pile[i + j] for j in range(4))
                game_state.recently_played.extend([pile[i], pile[i + 1], pile[i + 2], pile[i + 3]])

                del pile[i + 3]
                del pile[i + 2]
                del pile[i + 1]
                copy_card = pile[i]
                del pile[i]
                game_state.quads = True
                game_state.quads = False
                return Card(1, 'clear'), pile
    return prev_card, pile


def play_single(game_state, prev_card, pile):
    last = prev_card.value
    playing = prev_card
    
    # First look and see if two of the same value was played, and you have the other two
    if game_state.same_card_counter == 1 and len(pile) > 1:
        for i in range(len(pile) - 1):
            if pile[i].value == prev_card.value and pile[i].value == pile[i + 1].value:
                playing = pile[i]
                if game_state.display_mode: print(pile[i + 1])
                game_state.doubles = True
                game_state.same_card_counter = 2
                game_state.recently_played.extend([pile[i], pile[i + 1]])
                del pile[i + 1]
                del pile[i]
                if len(pile) == 0:
                    game_state.Final_Card = playing
                    return Card(15, 'all out'), pile
                return playing, pile

    # Second try to play non-two cards
    for card in pile:
        if card.value > last - 1 and card.value != 2:
            playing = card
            game_state.recently_played.append(card)
            pile.remove(card)
            break

    if len(pile) == 0:
        game_state.Final_Card = playing
        return Card(15, 'all out'), pile

    return playing, pile


def play_pair(game_state, prev_card, pile):
    playing = prev_card

    # Can only play pairs on pairs or on a clear card
    if prev_card.color != 'clear' and not game_state.pair_mode:
        return playing, pile, False, False

    if len(pile) <= 1: return playing, pile, False, False

    # First try to play non-two pairs
    for i in range(len(pile) - 1):
        if pile[i].value >= prev_card.value and pile[i].value != 2:
            if pile[i].value == pile[i+1].value:
                playing = pile[i]
                if game_state.display_mode: print(pile[i + 1])
                game_state.recently_played.extend([pile[i], pile[i + 1]])
                del pile[i+1]
                del pile[i]

                if len(pile) == 0:
                    game_state.Final_Card = playing
                    return Card(15, 'all out'), pile, False, False

                # If this pair completes a set of 4 (matches previous pair)
                if playing.value == prev_card.value:
                    if game_state.display_mode: print(playing)
                    # Clear the board and let the player play again
                    playing = Card(1, 'clear')
                    game_state.clear_recently_played()  # Clear recently played when board is cleared
                    playing, pile, pair, trio = one_turn(game_state, playing, pile, False, False)
                    return playing, pile, pair, trio

                return playing, pile, True, False

    return playing, pile, False, False


def play_trio(game_state, prev_card, pile):
    playing = prev_card

    # Can only play triples on triples or on a clear card
    if prev_card.color != 'clear' and not game_state.triple_mode:
        return playing, pile, False

    for card in pile:
        if card.value == prev_card.value:
            playing = card
            game_state.recently_played.append(card)
            del pile[pile.index(card)]
            game_state.same_card_counter = 2
            return playing, pile, False

    if len(pile) < 3: return playing, pile, False

    # First try to play non-two triples
    for i in range(len(pile) - 2):
        if pile[i].value >= prev_card.value and pile[i].value != 2:
            if pile[i].value == pile[i+2].value:
                playing = pile[i]
                if game_state.display_mode:
                    print(pile[i + 2])
                    print(pile[i + 1])
                game_state.recently_played.extend([pile[i], pile[i + 1], pile[i + 2]])
                del pile[i+2]
                del pile[i+1]
                del pile[i]

                if len(pile) == 0:
                    game_state.Final_Card = playing
                    return Card(15, 'all out'), pile, False

                return playing, pile, True

    return playing, pile, False


def play_all_twos(game_state, prev_card, pile):
    return Card(15, 'all done'), [], False, False


def one_turn(game_state, prev_card, pile, pair, trio):
    playing = prev_card

    if len(pile) == 0:
        game_state.Final_Card = playing
        return Card(15, 'all out'), pile, False, False
    # Check if we have a two at the start
    has_two_at_start = pile[0].value == 2
    if has_two_at_start and len(pile) > 1 and pile[-2].value == 2:
        game_state.Final_Card = pile[-1]
        return play_all_twos(game_state, prev_card, pile)
    
    if trio:
        playing, pile, trio = play_trio(game_state, prev_card, pile)
        if playing == prev_card: trio = True
    elif pair:
        playing, pile, pair, trio = play_pair(game_state, prev_card, pile)
        if playing == prev_card: pair = True
    elif prev_card.color == 'clear':
        playing, pile = quads(game_state, prev_card, pile)
        trio_hold = trio
        playing, pile, trio = play_trio(game_state, prev_card, pile)
        if playing == prev_card: trio = trio_hold
        if trio == False:
            playing, pile, pair, trio = play_pair(game_state, prev_card, pile)
            if (pair == False):
                playing, pile = play_single(game_state, prev_card, pile)
    else:
        playing, pile = play_single(game_state, prev_card, pile)

    # If we couldn't play anything and we have a two at the start
    if playing == prev_card and has_two_at_start:
        # Play the two and set it as the playing card
        playing = pile[0]  # Set the two as the playing card
        if game_state.display_mode: print(pile[0])
        game_state.recently_played.append(pile[0])
        pile.remove(pile[0])  # Remove the two
        game_state.bomb = True
        if len(pile) == 0:
            game_state.Final_Card = playing
            return Card(15, 'all out'), pile, False, False
        
        # After playing a two, let the player play any card
        playing, pile, pair, trio = one_turn(game_state, Card(1, 'clear'), pile, False, False)

    return playing, pile, pair, trio


def simulate_round(game_state, pile1, pile2, pile3, pile4):
    pile1 = organize_cards(pile1)
    pile2 = organize_cards(pile2)
    pile3 = organize_cards(pile3)
    pile4 = organize_cards(pile4)
    current_card = Card(1, 'clear')
    played_card = current_card

    skip_counter = 0
    pair_played = False
    trio_played = False
    game_state.clear_recently_played() 

    while True:
        current_pile = [pile1, pile2, pile3, pile4][game_state.player_turn]
        if game_state.display_mode: print(f'player {game_state.player_turn + 1}:')
        played_card, current_pile, pair_played, trio_played = one_turn(game_state, current_card, current_pile, pair_played, trio_played)
        if game_state.display_mode: print('skip' if played_card == current_card else played_card)
        
        # Update the correct pile
        if game_state.player_turn == 0:
            pile1 = current_pile
        elif game_state.player_turn == 1:
            pile2 = current_pile
        elif game_state.player_turn == 2:
            pile3 = current_pile
        else:
            pile4 = current_pile

        if played_card.value == 15:
            break

        if played_card == current_card:
            skip_counter += 1
            if skip_counter == 3:
                skip_counter = 0
                played_card = Card(1, 'clear')
                pair_played = False
                trio_played = False
                game_state.reset_modes()
                game_state.same_card_counter = 0
        else:
            skip_counter = 0
            if current_card.value == played_card.value: 
                game_state.player_turn += 1
                game_state.same_card_counter += 1
                skip_counter += 1
                if game_state.same_card_counter >= 3:
                    game_state.same_card_counter = 0
                    game_state.player_turn -= 2
                    played_card = Card(1, 'clear')
                    skip_counter = 0
            else: 
                game_state.same_card_counter = 0
            # If a 2 was played, reset everything immediately
            if played_card.value == 2:
                game_state.reset_modes()
                pair_played = False
                trio_played = False
                played_card = Card(1, 'clear')
            # Otherwise update game mode based on what was played
            else:
                if pair_played:
                    game_state.pair_mode = True
                    game_state.triple_mode = False
                elif trio_played:
                    game_state.pair_mode = False
                    game_state.triple_mode = True
                elif played_card.color == 'clear':  # If board was cleared
                    game_state.reset_modes()
                    pair_played = False
                    trio_played = False
        game_state.player_turn = (game_state.player_turn + 1) % 4
        current_card = played_card
        game_state.clear_recently_played()

    return game_state.player_turn + 1



if __name__ == '__main__':
    game_state = GameState()
    
    # Set display mode to False for simulations
    game_state.display_mode = False
    
    # Set game mechanics
    enable_choose = True
    enable_swap = True
    enable_winner_starts = True
    
    # Open CSV file for writing results
    with open('simulation_results.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        print("Writing headers to CSV file...")
        csvwriter.writerow(['choose_enabled', 'swap_enabled', 'winner_starts_enabled', 'player1_won'])
        
        # Run 10000 simulations
        for i in range(100000):
            deck = create_cards()
            pile1, pile2, pile3, pile4 = split_deck(deck)
            
            enable_choose = random.choice([True, False])
            enable_swap = random.choice([True, False])
            enable_winner_starts = random.choice([True, False])
            
            # Choose deck
            if enable_choose:
                pile1, pile2, pile3, pile4 = choose_deck(pile1, pile2, pile3, pile4)
            if enable_swap:
                swap_cards(pile1, [pile2, pile3, pile4][random.randint(0, 2)])
            game_state.player_turn = 0 if enable_winner_starts else random.randint(0, 3)
            
            game_state.copy_piles(pile1, pile2, pile3, pile4)
            winner = simulate_round(game_state, pile1, pile2, pile3, pile4)
            
            # Write result to CSV
            player1_won = 1 if winner == 1 else 0
            csvwriter.writerow([enable_choose, enable_swap, enable_winner_starts, player1_won])
            
            if (i + 1) % 10000 == 0:
                print(f"Completed {i + 1} simulations")
