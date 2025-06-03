import random
import tkinter as tk
import copy
import sys

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

SUIT_SYMBOLS = {
    'hearts':   '♥',
    'diamonds': '♦',
    'clubs':    '♣',
    'spades':   '♠',
    'clear': 'O',
    'all out':    '🎉'
}
SUIT_COLORS = {
    'hearts':   'red',
    'diamonds': 'red',
    'clubs':    'black',
    'spades':   'black',
    'clear':    'white',
    'all out':    'blue'
}

def draw_card(canvas, card, x0, y0, w=80 * 4, h=120 * 4, grayed_out=False, recently_played=False):
    """Draw one card at (x0,y0) size w×h."""
    # 1) white background & black border
    if recently_played:
        fill_color = 'lightblue'
    else:
        fill_color = 'lightgray' if grayed_out else 'white'
    canvas.create_rectangle(x0, y0, x0+w, y0+h,
                            outline='black', width=2, fill=fill_color)
    # 2) rank top-left
    col = SUIT_COLORS[card.color]
    if grayed_out and not recently_played:
        col = 'gray'
    copy_card = copy.deepcopy(card)

    if card.value == 11:
        copy_card.value = 'J'
    if card.value == 12:
        copy_card.value = 'Q'
    if card.value == 13:
        copy_card.value = 'K'
    if card.value == 14:
        copy_card.value = 'A'

    canvas.create_text(x0+20, y0+20,
                       text=str(copy_card.value),
                       anchor='nw',
                       fill=col,
                       font=('Arial', int(w/5), 'bold'))
    # 3) suit symbol center
    sym = SUIT_SYMBOLS[card.color]
    canvas.create_text(x0 + w/2, y0 + h/2,
                       text=sym,
                       fill=col,
                       font=('Arial', int(w*0.6)))
    # 4) rank bottom-right
    canvas.create_text(x0+w-20, y0+h-20,
                       text=str(copy_card.value),
                       anchor='se',
                       fill=col,
                       font=('Arial', int(w/5), 'bold'))



def show_state(game_state, current_card, playing_card, skip, doubles, triples, players_hand):
    """
    Pop-up showing:
      • Current card (left)
      • Playing card (right)
      • skip flag, doubles flag
      • which player's turn at bottom
    """
    if not game_state.display_mode:
        return
        
    root = tk.Tk()
    root.bind("<Escape>", lambda e: sys.exit())

    root.title(f"Player {game_state.player_turn + 1}'s turn")

    # make enough space for two cards + text
    canvas = tk.Canvas(root, width=296 * 4, height=220 * 4, bg='lightgray')
    canvas.pack(padx=10 * 4, pady=10 * 4)

    # Common card display settings
    card_w, card_h = 70, 110  # size of each hand‐card
    spacing = 20  # gap between cards
    y0 = (200 * 4) - card_h - 20  # 20px margin from bottom

    # draw current on left, playing on right
    # If this turn was a skip, just display "skip" and skip the card drawings
    if playing_card.value == 15:
        canvas.create_text(150 * 4, 75 * 4, text=f"{game_state.player_turn + 1} Wins", font=('Arial', 24 * 4, 'bold'), fill='pink')
        canvas.create_text(150 * 4, 400, text=f"{game_state.player_turn + 1}'s original pile:", font=('Arial', 24, 'bold'), fill='black')
        draw_card(canvas, game_state.Final_Card, x0=200 * 4, y0=30 * 4, grayed_out=False)
        pile = game_state.get_orig_pile(game_state.player_turn)
        for idx, c in enumerate(organize_cards(pile)):
            x0 = 20 + idx * (card_w + spacing)  # start 20px in, then space out
            draw_card(canvas, c, x0=x0, y0=y0, w=card_w, h=card_h)
    elif skip:
        canvas.create_text(150 * 4, 75 * 4, text = f"{game_state.player_turn + 1} Skips", font = ('Arial', 24 * 4, 'bold'), fill='gray')
        # Draw the original pile with played cards grayed out
        orig_pile = game_state.get_orig_pile(game_state.player_turn)
        for idx, c in enumerate(organize_cards(orig_pile)):
            x0 = 20 + idx * (card_w + spacing)
            # Check if card is still in player's hand
            is_played = not any(pc.value == c.value and pc.color == c.color for pc in players_hand)
            # Check if card was recently played
            was_recent = any(rc.value == c.value and rc.color == c.color for rc in game_state.recently_played)
            draw_card(canvas, c, x0=x0, y0=y0, w=card_w, h=card_h, 
                     grayed_out=is_played, recently_played=was_recent)
    else:
        # draw current on left, playing on right
        canvas.create_text(60 * 4, 40, text="Previous Card", font=('Arial', 12 * 4, 'underline'))
        canvas.create_text(240 * 4, 40, text="Played Card", font=('Arial', 12 * 4, 'underline'))
        if triples:
            draw_card(canvas, playing_card, x0=188 * 4, y0=20 * 4)
            draw_card(canvas, playing_card, x0=194 * 4, y0=25 * 4)
            if current_card.value != 1 and not game_state.bomb:
                draw_card(canvas, current_card, x0=8 * 4, y0=20 * 4)
                draw_card(canvas, current_card, x0=14 * 4, y0=25 * 4)
        elif doubles:
            draw_card(canvas, playing_card, x0=190 * 4, y0=20 * 4, w=60 * 4, h=90 * 4)
            if current_card.value != 1 and not game_state.bomb:
                draw_card(canvas, current_card, x0=10 * 4, y0=20 * 4, w=60 * 4, h=90 * 4)
        if game_state.quads:
            draw_card(canvas, playing_card, x0=185 * 4, y0=18 * 4)
            draw_card(canvas, playing_card, x0=190 * 4, y0=22 * 4)
            draw_card(canvas, playing_card, x0=195 * 4, y0=26 * 4)

        draw_card(canvas, playing_card, x0=200 * 4, y0=30 * 4)
        canvas.create_text(150 * 4, 100,
            text=f"Player {game_state.player_turn + 1}'s turn",
            font=('Arial',12 * 3,'italic')
        )
        if game_state.bomb:
            canvas.create_text(150 * 4, 80 * 4, text="💣", font=('Arial', 40 * 4), fill='orange')
            canvas.create_text(150 * 4, 50 * 4, text="2 was played", font=('Arial', 40, 'bold'), fill='black')
        game_state.bomb = False

        # Draw the original pile with played cards grayed out or highlighted
        orig_pile = game_state.get_orig_pile(game_state.player_turn)
        for idx, c in enumerate(organize_cards(orig_pile)):
            x0 = 20 + idx * (card_w + spacing)
            # Check if card is still in player's hand
            is_played = not any(pc.value == c.value and pc.color == c.color for pc in players_hand)
            # Check if card was recently played
            was_recent = any(rc.value == c.value and rc.color == c.color for rc in game_state.recently_played)
            draw_card(canvas, c, x0=x0, y0=y0, w=card_w, h=card_h, 
                     grayed_out=is_played, recently_played=was_recent)

    draw_card(canvas, current_card, x0=20 * 4, y0=30 * 4)
    root.bind("<Return>", lambda event: root.destroy())
    root.mainloop()


def create_cards():
    colors = ['hearts', 'diamonds', 'spades', 'clubs']
    deck = [Card(value, color) for value in range(2, 15) for color in colors]
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
                if game_state.display_mode: 
                    for j in range(4):
                        print(pile[i + j])
                game_state.recently_played.extend([pile[i], pile[i + 1], pile[i + 2], pile[i + 3]])

                del pile[i + 3]
                del pile[i + 2]
                del pile[i + 1]
                copy_card = pile[i]
                del pile[i]
                game_state.quads = True
                show_state(game_state, prev_card, copy_card, False, False, False, pile)
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
                    show_state(game_state, prev_card, playing, False, True, False, pile)
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
            show_state(game_state, current_card, played_card, False, pair_played, trio_played, [])
            break

        if played_card == current_card:
            skip_counter += 1
            show_state(game_state, current_card, played_card, True, pair_played, trio_played, current_pile)
            if skip_counter == 3:
                skip_counter = 0
                played_card = Card(1, 'clear')
                pair_played = False
                trio_played = False
                game_state.reset_modes()
                game_state.same_card_counter = 0
        else:
            skip_counter = 0
            show_state(game_state, current_card, played_card, False, pair_played, trio_played, current_pile)
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
    
    # Prompt for display mode
    display_mode = input("Would you like to enable display mode? Press 'y' for yes: ")
    game_state.display_mode = display_mode.upper() == 'Y'
    
    # Prompt for game mechanics
    print("\nWhich game mechanics would you like to enable?")
    print("1: Choose deck (top card of each deck is showed and winner picks their deck)")
    print("2: Winner gets to swap one card of their choosing with another player")
    print("3: Winner starts next round")
    print("4: All of the above")
    print("N: No mechanics")
    mechanics = input("Enter your choice (1-4 or N): ")
    
    enable_choose = True
    enable_swap = True
    enable_winner_starts = True
    
    if mechanics in ['1', '2', '3', '4']:
        enable_choose = mechanics in ['1', '4']
        enable_swap = mechanics in ['2', '4']
        enable_winner_starts = mechanics in ['3', '4']
    
    # If N or n is selected, disable all mechanics
    if mechanics.upper() == 'N':
        enable_choose = False
        enable_swap = False
        enable_winner_starts = False
    
    if not game_state.display_mode:
        iterations = int(input("How many games would you like to simulate? "))
        wins = [0, 0, 0, 0]  # Track wins for each player
        
        for i in range(iterations):
            deck = create_cards()
            pile1, pile2, pile3, pile4 = split_deck(deck)
            
            if enable_choose:
                pile1, pile2, pile3, pile4 = choose_deck(pile1, pile2, pile3, pile4)
            if enable_swap:
                swap_cards(pile1, [pile2, pile3, pile4][random.randint(0, 2)])
            game_state.player_turn = 0 if enable_winner_starts else random.randint(0, 3)
            
            game_state.copy_piles(pile1, pile2, pile3, pile4)
            winner = simulate_round(game_state, pile1, pile2, pile3, pile4)
            wins[winner - 1] += 1
            print(f"Game {i + 1}: Player {winner} wins!")
        
        print("\nFinal Results:")
        for i in range(4):
            win_percentage = (wins[i] / iterations) * 100
            print(f"Player {i + 1}: {wins[i]} wins ({win_percentage:.1f}%)")
    else:
        deck = create_cards()
        pile1, pile2, pile3, pile4 = split_deck(deck)
        
        if enable_choose:
            pile1, pile2, pile3, pile4 = choose_deck(pile1, pile2, pile3, pile4)
        if enable_swap:
            swap_cards(pile1, [pile2, pile3, pile4][random.randint(0, 2)])
        game_state.player_turn = 0 if enable_winner_starts else random.randint(0, 3)
            
        game_state.copy_piles(pile1, pile2, pile3, pile4)
        winner = simulate_round(game_state, pile1, pile2, pile3, pile4)
        print(f"Player {winner} wins!")
