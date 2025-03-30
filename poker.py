import tkinter as tk
from tkinter import messagebox
import random
from enum import Enum
from itertools import combinations

# Define card suits using Enum
class Suit(Enum):
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"

# Define the Card class
class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def __str__(self):
        value_str = {11: "J", 12: "Q", 13: "K", 14: "A"}.get(self.value, str(self.value))
        return f"{value_str}{self.suit.value}"

# Hand names for displaying hand strength
HAND_NAMES = [
    "High Card",
    "One Pair",
    "Two Pair",
    "Three of a Kind",
    "Straight",
    "Flush",
    "Full House",
    "Four of a Kind",
    "Straight Flush"
]

# Poker game class
class PokerGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Texas Hold'em Poker")
        self.master.geometry("800x600")
        self.master.configure(bg="#1a1a1a")  # Dark mode background

        # Game state variables
        self.deck = []
        self.player_hand = []
        self.computer_hand = []
        self.community_cards = []
        self.player_chips = 1000
        self.computer_chips = 1000
        self.pot = 0
        self.current_bet = 0
        self.player_bet = 0
        self.computer_bet = 0
        self.needs_to_act = []
        self.current_player = ""
        self.betting_round = 0
        self.folded = False
        self.folder = None  # Tracks who folded

        # Initialize GUI
        self.create_widgets()
        self.new_game()

    ### GUI Setup
    def create_widgets(self):
        self.master.option_add("*Background", "#1a1a1a")
        self.master.option_add("*Foreground", "white")

        self.top_frame = tk.Frame(self.master, bg="#1a1a1a")
        self.top_frame.pack(pady=10)

        self.center_frame = tk.Frame(self.master, bg="#1a1a1a")
        self.center_frame.pack(pady=10)

        self.bottom_frame = tk.Frame(self.master, bg="#1a1a1a")
        self.bottom_frame.pack(pady=10)

        tk.Label(self.top_frame, text="Community Cards", font=("Arial", 16), fg="cyan").pack()
        self.community_cards_frame = tk.Frame(self.top_frame, bg="#1a1a1a")
        self.community_cards_frame.pack()
        self.community_card_labels = [
            tk.Label(
                self.community_cards_frame, text="", width=5, height=2, bg="white", fg="black",
                relief="solid", borderwidth=2, highlightthickness=1, highlightbackground="cyan"
            ) for _ in range(5)
        ]
        for label in self.community_card_labels:
            label.pack(side="left", padx=5)

        tk.Label(self.center_frame, text="Your Hand", font=("Arial", 16), fg="cyan").pack()
        self.player_hand_frame = tk.Frame(self.center_frame, bg="#1a1a1a")
        self.player_hand_frame.pack()
        self.player_card_labels = [
            tk.Label(
                self.player_hand_frame, text="", width=5, height=2, bg="white", fg="black",
                relief="solid", borderwidth=2, highlightthickness=1, highlightbackground="cyan"
            ) for _ in range(2)
        ]
        for label in self.player_card_labels:
            label.pack(side="left", padx=5)

        tk.Label(self.center_frame, text="Computer's Hand", font=("Arial", 16), fg="cyan").pack()
        self.computer_hand_frame = tk.Frame(self.center_frame, bg="#1a1a1a")
        self.computer_hand_frame.pack()
        self.computer_card_labels = [
            tk.Label(
                self.computer_hand_frame, text="??", width=5, height=2, bg="white", fg="black",
                relief="solid", borderwidth=2, highlightthickness=1, highlightbackground="cyan"
            ) for _ in range(2)
        ]
        for label in self.computer_card_labels:
            label.pack(side="left", padx=5)

        self.controls_frame = tk.Frame(self.bottom_frame, bg="#1a1a1a")
        self.controls_frame.pack()

        self.action1_button = tk.Button(self.controls_frame, text="Check", command=lambda: self.player_action("check"))
        self.action1_button.pack(side="left", padx=5)

        self.action2_button = tk.Button(self.controls_frame, text="Bet", command=lambda: self.player_action("bet"))
        self.action2_button.pack(side="left", padx=5)

        self.fold_button = tk.Button(self.controls_frame, text="Fold", command=lambda: self.player_action("fold"))
        self.fold_button.pack(side="left", padx=5)

        self.turn_label = tk.Label(self.controls_frame, text="", font=("Arial", 14), fg="cyan")
        self.turn_label.pack(pady=10)

        self.message_label = tk.Label(self.bottom_frame, text="", font=("Arial", 12))
        self.message_label.pack(pady=10)

        self.player_chips_label = tk.Label(self.bottom_frame, text=f"Player chips: {self.player_chips}", font=("Arial", 12))
        self.player_chips_label.pack(side="left", padx=10)

        self.computer_chips_label = tk.Label(self.bottom_frame, text=f"Computer chips: {self.computer_chips}", font=("Arial", 12))
        self.computer_chips_label.pack(side="right", padx=10)

        self.pot_label = tk.Label(self.bottom_frame, text=f"Pot: {self.pot}", font=("Arial", 12))
        self.pot_label.pack()

    ### Game Logic
    def new_game(self):
        """Start a new hand."""
        self.deck = [Card(suit, value) for suit in Suit for value in range(2, 15)]
        random.shuffle(self.deck)
        self.player_hand = [self.deck.pop(), self.deck.pop()]
        self.computer_hand = [self.deck.pop(), self.deck.pop()]
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.player_bet = 0
        self.computer_bet = 0
        self.folded = False
        self.folder = None
        self.betting_round = 0
        self.message_label.config(text="")
        self.update_card_labels()
        self.start_betting_round()

    def update_card_labels(self):
        """Update the displayed cards."""
        for i, card in enumerate(self.player_hand):
            self.player_card_labels[i].config(text=str(card))
        for label in self.computer_card_labels:
            label.config(text="??")
        for label in self.community_card_labels:
            label.config(text="")

    def start_betting_round(self):
        """Begin a betting round."""
        self.needs_to_act = ["player", "computer"]
        self.current_player = "player"
        self.update_turn_label()
        self.update_button_texts()
        self.enable_player_buttons()

    def update_turn_label(self):
        """Update the turn indicator."""
        self.turn_label.config(text="Your turn" if self.current_player == "player" else "Computer's turn", fg="cyan")

    def update_button_texts(self):
        """Update action button texts based on game state."""
        self.action1_button.config(text="Check" if self.current_bet == self.player_bet else "Call")
        self.action2_button.config(text="Bet" if self.current_bet == 0 else "Raise")

    def enable_player_buttons(self):
        """Enable player action buttons."""
        self.action1_button.config(state="normal")
        self.action2_button.config(state="normal")
        self.fold_button.config(state="normal")

    def disable_player_buttons(self):
        """Disable player action buttons."""
        self.action1_button.config(state="disabled")
        self.action2_button.config(state="disabled")
        self.fold_button.config(state="disabled")

    def player_action(self, action):
        """Handle player actions."""
        if action == "fold":
            self.folder = "player"
            self.folded = True
            self.end_betting_round()
        elif action == "check":
            if self.current_bet == self.player_bet:
                self.needs_to_act.remove("player")
                if not self.needs_to_act:
                    self.end_betting_round()
                else:
                    self.current_player = "computer"
                    self.update_turn_label()
                    self.disable_player_buttons()
                    self.master.after(1000, self.computer_action)
            else:
                self.message_label.config(text="Invalid Action: You cannot check. You must call or fold.", fg="yellow")
                return
            #staring bet
        elif action == "bet" and self.current_bet == 0:
            self.player_bet += 10
            self.current_bet = self.player_bet
            self.player_chips -= 10
            self.pot += 10
            self.handle_action("player", "bet")
        elif action == "bet" or action == "raise":
            self.player_bet = self.current_bet + 10
            self.current_bet = self.player_bet
            self.player_chips -= 10
            self.pot += 10
            self.handle_action("player", "raise")
        self.update_labels()
        self.message_label.config(text="")

    def handle_action(self, player, action_type):
        """Process an action and advance the game state."""
        self.needs_to_act.remove(player)
        if action_type in ("bet", "raise") and "computer" not in self.needs_to_act:
            self.needs_to_act.append("computer")
        self.current_player = "computer"
        self.update_turn_label()
        self.disable_player_buttons()
        self.master.after(1000, self.computer_action)

    def computer_action(self):
        """Handle computer actions with modified behavior to fold in river round if there's a bet."""
        if self.folded:
            return
        if self.betting_round == 3:  # River round
            if self.current_bet > self.computer_bet:
                # Fold if there is a bet to call
                self.folder = "computer"
                self.folded = True
                self.end_betting_round()
            else:
                # Check if no bet to call
                self.needs_to_act.remove("computer")
                if not self.needs_to_act:
                    self.end_betting_round()
                else:
                    self.current_player = "player"
                    self.update_turn_label()
                    self.enable_player_buttons()
        else:
            # Original logic for pre-flop, flop, turn
            if random.random() < 0.5 and self.current_bet > self.computer_bet:
                amount_to_call = self.current_bet - self.computer_bet
                self.computer_bet = self.current_bet
                self.computer_chips -= amount_to_call
                self.pot += amount_to_call
                self.needs_to_act.remove("computer")
                if not self.needs_to_act:
                    self.end_betting_round()
                else:
                    self.current_player = "player"
                    self.update_turn_label()
                    self.enable_player_buttons()
            elif self.current_bet == self.computer_bet:
                self.needs_to_act.remove("computer")
                if not self.needs_to_act:
                    self.end_betting_round()
                else:
                    self.current_player = "player"
                    self.update_turn_label()
                    self.enable_player_buttons()
            else:
                self.folder = "computer"
                self.folded = True
                self.end_betting_round()
        self.update_labels()

    def end_betting_round(self):
        """End the current betting round and proceed."""
        self.betting_round += 1
        if self.folded:
            if self.folder == "player":
                winner = "computer"
            else:
                winner = "player"
            self.award_pot(winner)
        elif self.betting_round == 1:
            self.deal_flop()
            self.start_betting_round()
        elif self.betting_round == 2:
            self.deal_turn()
            self.start_betting_round()
        elif self.betting_round == 3:
            self.deal_river()
            self.start_betting_round()
        elif self.betting_round == 4:
            self.showdown()

    def deal_flop(self):
        """Deal three community cards (flop)."""
        self.community_cards.extend([self.deck.pop(), self.deck.pop(), self.deck.pop()])
        for i in range(3):
            self.community_card_labels[i].config(text=str(self.community_cards[i]))

    def deal_turn(self):
        """Deal the fourth community card (turn)."""
        self.community_cards.append(self.deck.pop())
        self.community_card_labels[3].config(text=str(self.community_cards[3]))

    def deal_river(self):
        """Deal the fifth community card (river)."""
        self.community_cards.append(self.deck.pop())
        self.community_card_labels[4].config(text=str(self.community_cards[4]))

    def showdown(self):
        """Reveal hands and determine the winner."""
        for i, card in enumerate(self.computer_hand):
            self.computer_card_labels[i].config(text=str(card))
        player_hand = self.get_best_hand(self.player_hand, self.community_cards)
        computer_hand = self.get_best_hand(self.computer_hand, self.community_cards)
        if player_hand > computer_hand:
            self.message_label.config(text="You win!", fg="green")
            self.player_chips += self.pot
        elif computer_hand > player_hand:
            self.message_label.config(text="Computer wins!", fg="red")
            self.computer_chips += self.pot
        else:
            self.message_label.config(text="Tie!", fg="yellow")
            self.player_chips += self.pot // 2
            self.computer_chips += self.pot // 2
        self.update_labels()
        self.master.after(2000, self.ask_to_continue)

    def award_pot(self, winner):
        remaining_cards = 5 - len(self.community_cards)
        temp_community = [self.deck.pop() for _ in range(remaining_cards)]
        full_community = self.community_cards + temp_community

            # Evaluate best hands
        player_best = self.get_best_hand(self.player_hand, full_community)
        computer_best = self.get_best_hand(self.computer_hand, full_community)
        for i, card in enumerate(self.computer_hand):
            self.computer_card_labels[i].config(text=str(card))

            # Get hand names from rankings
        self.player_hand_name = HAND_NAMES[player_best[0]]
        self.computer_hand_name = HAND_NAMES[computer_best[0]]
        """Award the pot to the winner when someone folds, with hand strength display when computer folds."""
        if winner == "player":
            # Deal remaining community cards temporarily for evaluation
           

            # Reveal computer's cards
           

            # Display win message with hand strengths
            self.message_label.config(
                text=f"You win, computer folded! Your hand: {self.player_hand_name}, Computer's hand: {self.computer_hand_name}",
                fg="green"
            )
            self.player_chips += self.pot
        if winner=="computer": # winner == "computer"
            self.message_label.config(text=f"Computer wins, you folded! Your hand: {self.player_hand_name}, Computer's hand: {self.computer_hand_name}", fg="red")
            self.computer_chips += self.pot
        self.update_labels()
        self.master.after(2000, self.ask_to_continue)

    ### Hand Evaluation
    def get_best_hand(self, hand, community):
        all_cards = hand + community
        best_hand = max(combinations(all_cards, 5), key=self.evaluate_hand)
        return self.evaluate_hand(best_hand)

    def evaluate_hand(self, hand):
        values = sorted([card.value for card in hand], reverse=True)
        suits = [card.suit for card in hand]
        flush = len(set(suits)) == 1
        straight = all(values[i] - 1 == values[i+1] for i in range(4)) or values == [14, 5, 4, 3, 2]

        if flush and straight:
            return (8, values)  # Straight Flush
        counts = [values.count(v) for v in set(values)]
        if 4 in counts:
            return (7, [v for v in set(values) if values.count(v) == 4][0])  # Four of a Kind
        if 3 in counts and 2 in counts:
            return (6, [v for v in set(values) if values.count(v) == 3][0])  # Full House
        if flush:
            return (5, values)  # Flush
        if straight:
            return (4, values)  # Straight
        if 3 in counts:
            return (3, [v for v in set(values) if values.count(v) == 3][0])  # Three of a Kind
        pairs = [v for v in set(values) if values.count(v) == 2]
        if len(pairs) == 2:
            return (2, sorted(pairs, reverse=True))  # Two Pair
        if len(pairs) == 1:
            return (1, pairs[0])  # One Pair
        return (0, values)  # High Card

    def update_labels(self):
        """Update chip and pot display."""
        self.player_chips_label.config(text=f"Player chips: {self.player_chips}")
        self.computer_chips_label.config(text=f"Computer chips: {self.computer_chips}")
        self.pot_label.config(text=f"Pot: {self.pot}")

    ### Continuation Prompt
    def ask_to_continue(self):
        self.master.update_idletasks()
        response = messagebox.askyesno("Continue?", "Do you want to play another round?")
        if response:
            self.new_game()
        else:
            self.master.destroy()

# Run the game
if __name__ == "__main__":
    root = tk.Tk()
    game = PokerGame(root)
    root.mainloop()