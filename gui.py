"""
Blackjack GUI
Single-file Python 3 Tkinter app.
How to run: `python blackjack_gui.py` (requires Python 3, no extra packages)

Features:
- Simple betting, Hit / Stand / New Round
- Dealer plays by standard rules (hit until 17)
- Aces counted as 1 or 11 optimally
- Basic bankroll tracking and bet entry
- Text log of actions and outcomes

This is intentionally straightforward so you can expand (split cards to images, add splits/double down, animations, etc.)
"""

import tkinter as tk
from tkinter import messagebox
import random

# --- Game logic ---

SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

class Deck:
    def __init__(self):
        self.cards = [(r, s) for s in SUITS for r in RANKS]
        random.shuffle(self.cards)

    def deal(self):
        if not self.cards:
            self.__init__()
        return self.cards.pop()


def value_of_hand(hand):
    # hand: list of (rank, suit)
    vals = 0
    aces = 0
    for r, _ in hand:
        if r in ['J','Q','K']:
            vals += 10
        elif r == 'A':
            aces += 1
            vals += 11
        else:
            vals += int(r)
    # reduce aces from 11 to 1 if needed
    while vals > 21 and aces:
        vals -= 10
        aces -= 1
    return vals

# --- GUI / Controller ---

class BlackjackApp:
    def __init__(self, root):
        self.root = root
        root.title('BlackJack — Simple GUI')

        self.deck = Deck()
        self.player = []
        self.dealer = []
        self.in_round = False

        # bankroll and bet
        self.bankroll = 1000
        self.bet = 10

        # top frame: dealer and player cards
        self.frame_cards = tk.Frame(root)
        self.frame_cards.pack(padx=10, pady=8, fill='x')

        self.lbl_dealer_title = tk.Label(self.frame_cards, text='Dealer')
        self.lbl_dealer_title.pack()
        self.txt_dealer = tk.Label(self.frame_cards, text='', font=('Courier', 14))
        self.txt_dealer.pack()

        self.lbl_player_title = tk.Label(self.frame_cards, text='Player')
        self.lbl_player_title.pack()
        self.txt_player = tk.Label(self.frame_cards, text='', font=('Courier', 14))
        self.txt_player.pack()

        # middle frame: controls
        self.frame_controls = tk.Frame(root)
        self.frame_controls.pack(padx=10, pady=8)

        self.btn_hit = tk.Button(self.frame_controls, text='Hit', command=self.hit, state='disabled', width=10)
        self.btn_hit.grid(row=0, column=0, padx=6)
        self.btn_stand = tk.Button(self.frame_controls, text='Stand', command=self.stand, state='disabled', width=10)
        self.btn_stand.grid(row=0, column=1, padx=6)
        self.btn_new = tk.Button(self.frame_controls, text='New Round', command=self.new_round, width=10)
        self.btn_new.grid(row=0, column=2, padx=6)

        # betting controls
        self.frame_bet = tk.Frame(root)
        self.frame_bet.pack(padx=10, pady=6)
        tk.Label(self.frame_bet, text='Bankroll:').grid(row=0, column=0, sticky='e')
        self.lbl_bankroll = tk.Label(self.frame_bet, text=str(self.bankroll))
        self.lbl_bankroll.grid(row=0, column=1, sticky='w', padx=(4,12))

        tk.Label(self.frame_bet, text='Bet:').grid(row=0, column=2, sticky='e')
        self.ent_bet = tk.Entry(self.frame_bet, width=8)
        self.ent_bet.insert(0, str(self.bet))
        self.ent_bet.grid(row=0, column=3, padx=(4,0))

        # log
        self.txt_log = tk.Text(root, height=8, state='disabled', wrap='word')
        self.txt_log.pack(padx=10, pady=8, fill='both', expand=True)

        # shortcut: double-click new round to auto bet last
        self.btn_new.bind('<Double-1>', lambda e: self.new_round())

        self._update_ui()

    def log(self, *parts):
        self.txt_log.config(state='normal')
        self.txt_log.insert('end', ' '.join(map(str, parts)) + '\n')
        self.txt_log.see('end')
        self.txt_log.config(state='disabled')

    def _render_hand(self, hand):
        return '  '.join([f'{r}{s}' for r,s in hand])

    def _update_ui(self):
        # update labels
        if self.in_round:
            # hide dealer second card
            if len(self.dealer) >= 2:
                displayed = f'{self.dealer[0][0]}{self.dealer[0][1]}  ??'
            else:
                displayed = self._render_hand(self.dealer)
            self.txt_dealer.config(text=displayed)
        else:
            self.txt_dealer.config(text=self._render_hand(self.dealer) + (f'  ({value_of_hand(self.dealer)})' if self.dealer else ''))

        self.txt_player.config(text=self._render_hand(self.player) + (f'  ({value_of_hand(self.player)})' if self.player else ''))
        self.lbl_bankroll.config(text=str(self.bankroll))

    def new_round(self):
        if self.in_round:
            self.log('Round already in progress.')
            return

        # read bet
        try:
            b = int(self.ent_bet.get())
            if b <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror('Invalid bet', 'Please enter a positive integer bet.')
            return

        if b > self.bankroll:
            messagebox.showerror('Insufficient bankroll', 'You cannot bet more than your bankroll.')
            return

        self.bet = b
        self.bankroll -= b
        self.player = [self.deck.deal(), self.deck.deal()]
        self.dealer = [self.deck.deal(), self.deck.deal()]
        self.in_round = True
        self.log(f'New round — bet {self.bet}')
        self.log('Player:', self._render_hand(self.player), '->', value_of_hand(self.player))
        self.log('Dealer shows:', f'{self.dealer[0][0]}{self.dealer[0][1]}')

        # blackjack check
        pv = value_of_hand(self.player)
        dv = value_of_hand(self.dealer)
        if pv == 21 and dv != 21:
            # natural blackjack (pays 3:2)
            winnings = int(self.bet * 2.5)
            self.bankroll += winnings
            self.log('Blackjack! You win', winnings)
            self.in_round = False
        elif pv == 21 and dv == 21:
            self.bankroll += self.bet
            self.log('Both have Blackjack. Push.')
            self.in_round = False
        else:
            self.btn_hit.config(state='normal')
            self.btn_stand.config(state='normal')

        self._update_ui()

    def hit(self):
        if not self.in_round:
            return
        card = self.deck.deal()
        self.player.append(card)
        self.log('Player hits:', f'{card[0]}{card[1]}', '->', value_of_hand(self.player))
        if value_of_hand(self.player) > 21:
            self.log('Player busted!')
            self.in_round = False
            self._end_round()
        self._update_ui()

    def stand(self):
        if not self.in_round:
            return
        self.log('Player stands with', value_of_hand(self.player))
        self.btn_hit.config(state='disabled')
        self.btn_stand.config(state='disabled')
        self._dealer_play()

    def _dealer_play(self):
        # dealer reveals and plays
        self.log('Dealer reveals:', self._render_hand(self.dealer), '->', value_of_hand(self.dealer))
        while value_of_hand(self.dealer) < 17:
            card = self.deck.deal()
            self.dealer.append(card)
            self.log('Dealer hits:', f'{card[0]}{card[1]}', '->', value_of_hand(self.dealer))
        if value_of_hand(self.dealer) > 21:
            self.log('Dealer busted!')
        else:
            self.log('Dealer stands with', value_of_hand(self.dealer))
        self.in_round = False
        self._end_round()

    def _end_round(self):
        pv = value_of_hand(self.player)
        dv = value_of_hand(self.dealer)
        result = ''
        if pv > 21:
            result = 'lose'
        elif dv > 21:
            result = 'win'
        elif pv > dv:
            result = 'win'
        elif pv == dv:
            result = 'push'
        else:
            result = 'lose'

        if result == 'win':
            winnings = self.bet * 2
            self.bankroll += winnings
            self.log('You win!', 'Winnings:', winnings)
        elif result == 'push':
            self.bankroll += self.bet
            self.log('Push: bet returned.')
        else:
            self.log('You lost the bet.')

        # cleanup UI
        self.btn_hit.config(state='disabled')
        self.btn_stand.config(state='disabled')
        self._update_ui()

        # check bankroll
        if self.bankroll <= 0:
            self.log('Bankroll exhausted. Reset to 1000 for fun.')
            self.bankroll = 1000
        
# --- Run app ---

if __name__ == '__main__':
    root = tk.Tk()
    app = BlackjackApp(root)
    root.mainloop()
