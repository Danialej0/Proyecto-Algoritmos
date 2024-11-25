"""
    JERONIMO ARGUELLO
    JUAN BAHOS
    DANIEL MORENO

"""

import os
import random
import tkinter as tk
from tkinter import messagebox, Toplevel
from PIL import Image, ImageTk

#Backend: 
class Card:
    def __init__(self, pinta, rango, value):
        self.pinta = pinta
        self.rango = rango
        self.value = value

    def __str__(self):
        return f"{self.rango}_of_{self.pinta}"


class Deck:
    def __init__(self):
        self.cards = []
        pintas = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        rangos = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
        values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 10, '10': 10,
                  'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11}
        for pinta in pintas:
            for rango in rangos:
                self.cards.append(Card(pinta, rango, values[rango]))
        random.shuffle(self.cards)

    def deal_card(self):
        return self.cards.pop()


class Hand:
    def __init__(self):
        self.cards = []
        self.value = 0
        self.aces = 0

    def add_card(self, card):
        self.cards.append(card)
        self.value += card.value
        if card.rango == 'Ace':
            self.aces += 1
        self.ajustar_Aces()

    def ajustar_Aces(self):
        while self.value > 21 and self.aces:
            self.value -= 10
            self.aces -= 1


class NodoHistorial:
    def __init__(self, bet, result, player_hand, dealer_hand):
        self.bet = bet
        self.result = result
        self.player_hand = player_hand
        self.dealer_hand = dealer_hand
        self.next = None


class Historial:
    def __init__(self):
        self.head = None

    def add_historial(self, bet, result, player_hand, dealer_hand):
        new_node = NodoHistorial(bet, result, player_hand, dealer_hand)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

    def get_Historial(self):
        records = []
        current = self.head
        while current:
            records.append({
                "bet": current.bet,
                "result": current.result,
                "player_hand": current.player_hand,
                "dealer_hand": current.dealer_hand
            })
            current = current.next
        return records

class ArbolProbabilidad:
    def __init__(self):
        self.card_values = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
            'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11
        }
    
    def calcular_probabilidad(self, dealer_hand, player_value, deck):
        """Calcula la probabilidad de ganar para el dealer"""
        if dealer_hand.value > 21:
            return 0.0
        
        # Si el dealer tiene más que el jugador y está entre 17-21, gana
        if dealer_hand.value >= 17 and dealer_hand.value <= 21 and dealer_hand.value > player_value:
            return 1.0
        
        # Si el dealer tiene 17 o más pero menos que el jugador, pierde
        if dealer_hand.value >= 17 and dealer_hand.value < player_value:
            return 0.0
        
        # Calcular probabilidades para cada carta faltante
        remaining_cards = self.num_cartas_faltantes(deck)
        total_cards = sum(remaining_cards.values())
        if total_cards == 0:
            return 0.0
            
        probability = 0.0
        for card_value, count in remaining_cards.items():
            if count > 0:
                # Probabilidad de sacar cierta carta
                card_prob = count / total_cards
                
                # Simular tomar esta carta
                new_hand = Hand()
                for card in dealer_hand.cards:
                    new_hand.add_card(card)
                new_hand.add_card(Card('Hearts', str(card_value), self.card_values[str(card_value)]))
                
                # Actualizar deck simulado
                new_deck = deck.cards.copy()
                new_deck.pop()
                
                # Calcular probabilidad recursivamente
                outcome_prob = self.calcular_probabilidad(new_hand, player_value, Deck())
                probability += card_prob * outcome_prob
                
        return probability
    
    def num_cartas_faltantes(self, deck):
        """Cuenta las cartas restantes en el mazo"""
        remaining = {str(i): 4 for i in range(2, 11)}
        remaining.update({'Jack': 4, 'Queen': 4, 'King': 4, 'Ace': 4})
        
        for card in deck.cards:
            remaining[card.rango] -= 1
            
        return remaining
    
    def should_hit(self, dealer_hand, player_value, deck):
        """Determina si el dealer debería pedir otra carta basado en probabilidades"""
        current_prob = self.calcular_probabilidad(dealer_hand, player_value, deck)
        
        # Simular tomar una carta
        simulated_hand = Hand()
        for card in dealer_hand.cards:
            simulated_hand.add_card(card)
        simulated_hand.add_card(deck.cards[-1])  # Simular la próxima carta
        
        hit_prob = self.calcular_probabilidad(simulated_hand, player_value, deck)
        
        return hit_prob > current_prob and dealer_hand.value < 21



#Frontend:
class Blackjack:
    def __init__(self, root):
        self.root = root
        self.root.title("Blackjack con Estilo")
        self.root.geometry("900x600")
        self.root.configure(bg="#2a7b4f")

        self.card_fotos = self.cargar_Imagen()
        self.historial = Historial()

        # variables
        self.deck = Deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.balance = 1000
        self.bet = 0

        #Top Frame
        self.info_frame = tk.Frame(self.root, bg="#004d26", pady=10, padx=10)
        self.info_frame.pack(fill="x")

        self.balance_label = tk.Label(self.info_frame, text=f"Saldo: {self.balance} Pecezuelos", font=("Arial", 16, "bold"),
                                      fg="white", bg="#004d26", padx=10)
        self.balance_label.pack(side="left")

        self.bet_label = tk.Label(self.info_frame, text=f"Apuesta: {self.bet} Pecezuelos", font=("Arial", 16, "bold"),
                                  fg="white", bg="#004d26", padx=10)
        self.bet_label.pack(side="left")

        self.bet_entry = tk.Entry(self.info_frame, font=("Arial", 14), width=10, justify="center")
        self.bet_entry.pack(side="left", padx=10)

        self.add_balance_button = tk.Button(self.info_frame, text="Añadir Saldo", command=self.add_balance,
                                            font=("Arial", 12, "bold"), bg="#4caf50", fg="white", width=12)
        self.add_balance_button.pack(side="right", padx=10)

        self.info_label = tk.Label(self.info_frame, text="Introduce tu apuesta y presiona 'Deal'.", font=("Arial", 14),
                                   fg="white", bg="#004d26")
        self.info_label.pack(side="right", padx=10)

        #Tabla 
        self.table_frame = tk.Frame(self.root, bg="#2a7b4f", pady=20)
        self.table_frame.pack(fill="both", expand=True)

        self.dealer_frame = tk.Frame(self.table_frame, bg="#2a7b4f", relief=tk.GROOVE, bd=3)
        self.dealer_frame.pack(side="top", pady=20)

        self.player_frame = tk.Frame(self.table_frame, bg="#2a7b4f", relief=tk.GROOVE, bd=3)
        self.player_frame.pack(side="bottom", pady=20)

        # botones
        self.button_frame = tk.Frame(self.root, bg="#004d26", pady=10)
        self.button_frame.pack(fill="x")

        self.deal_button = tk.Button(self.button_frame, text="Deal", command=self.deal_cards, font=("Arial", 12, "bold"),
                                     bg="#007b50", fg="white", width=12)
        self.deal_button.pack(side="left", padx=10)

        self.hit_button = tk.Button(self.button_frame, text="Pedir Carta", command=self.hit, font=("Arial", 12, "bold"),
                                    bg="#007b50", fg="white", width=12, state=tk.DISABLED)
        self.hit_button.pack(side="left", padx=10)

        self.stand_button = tk.Button(self.button_frame, text="Plantarse", command=self.stand, font=("Arial", 12, "bold"),
                                      bg="#007b50", fg="white", width=12, state=tk.DISABLED)
        self.stand_button.pack(side="left", padx=10)

        self.double_button = tk.Button(self.button_frame, text="Doblar Apuesta", command=self.doblar_Apuesta,
                                       font=("Arial", 12, "bold"), bg="#007b50", fg="white", width=12,
                                       state=tk.DISABLED)
        self.double_button.pack(side="left", padx=10)

        self.historial_button = tk.Button(self.button_frame, text="Historial", command=self.mostrar_Historial,
                                        font=("Arial", 12, "bold"), bg="#ffa500", fg="black", width=12)
        self.historial_button.pack(side="right", padx=10)


        self.actualizar_Etiquetas()
    
    def cargar_Imagen(self):
        """Carga las imágenes de las cartas en un diccionario."""
        card_dir = "./cards"
        card_fotos = {}
        for pinta in ['Hearts', 'Diamonds', 'Clubs', 'Spades']:
            for rango in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']:
                card_name = f"{rango}_of_{pinta}"
                card_path = os.path.join(card_dir, f"{card_name}.png")
                if os.path.exists(card_path):
                    image = Image.open(card_path).resize((100, 150))
                    card_fotos[card_name] = ImageTk.PhotoImage(image)
        return card_fotos

    def mostrar_Mano(self, frame, hand):
        """Muestra las cartas de una mano en el GUI."""
        for widget in frame.winfo_children():
            widget.destroy()
        
        for i, card in enumerate(hand.cards):
            card_image = self.card_fotos.get(str(card), None)
            card_container = tk.Frame(frame, width=100, height=150, bg="white", relief=tk.RAISED, bd=3)
            card_container.pack(side="left", padx=5, pady=5)

            if card_image:
                label = tk.Label(card_container, image=card_image, bg="white")
                label.image = card_image
                label.pack()

        # Agregar el número de mano
        hand_number_label = tk.Label(frame, text=f"Mano: {hand.value}", font=("Arial", 18, "bold"),
                                     fg="white", bg="green")
        hand_number_label.pack(side="bottom", pady=5)

    def actualizar_Etiquetas(self):
        """Actualiza saldo y apuesta."""
        self.balance_label.config(text=f"Saldo: {self.balance} Pecezuelos")
        self.bet_label.config(text=f"Apuesta: {self.bet} Pecezuelos")

    def add_balance(self):
        """Abre una ventana para ingresar el monto a añadir al saldo."""
        top = Toplevel(self.root)
        top.title("Añadir Saldo")
        top.geometry("300x150")

        amount_label = tk.Label(top, text="Monto a añadir:", font=("Arial", 12))
        amount_label.pack(pady=10)

        amount_entry = tk.Entry(top, font=("Arial", 14))
        amount_entry.pack(pady=10)

        def add_Cantidad():
            try:
                amount = int(amount_entry.get())
                if amount <= 0:
                    raise ValueError
                self.balance += amount
                self.actualizar_Etiquetas()
                top.destroy()
                messagebox.showinfo("Éxito", f"Se han añadido {amount} Pecezuelos.")
            except ValueError:
                messagebox.showerror("Error", "Por favor ingrese un monto válido.")

        add_button = tk.Button(top, text="Añadir", command=add_Cantidad, font=("Arial", 12, "bold"), bg="#007b50", fg="white")
        add_button.pack(pady=10)

    def deal_cards(self):
        """Inicia el juego y reparte las cartas."""
        try:
            self.bet = int(self.bet_entry.get())
            if self.bet > self.balance or self.bet <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Introduce una apuesta válida.")
            return

        self.balance -= self.bet
        self.actualizar_Etiquetas()

        # Resetear estado del juego
        self.deck = Deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()

        # Repartir cartas iniciales
        self.player_hand.add_card(self.deck.deal_card())
        self.player_hand.add_card(self.deck.deal_card())
        self.dealer_hand.add_card(self.deck.deal_card())
        self.dealer_hand.add_card(self.deck.deal_card())

        # Habilitar botones
        self.hit_button.config(state=tk.NORMAL)
        self.stand_button.config(state=tk.NORMAL)
        self.double_button.config(state=tk.NORMAL)
        self.deal_button.config(state=tk.DISABLED)
        self.info_label.config(text="Haz tu jugada.")

        self.actualizar_Display()

    def hit(self):
        """Pide una carta adicional al jugador."""
        self.player_hand.add_card(self.deck.deal_card())
        self.actualizar_Display()

        if self.player_hand.value > 21:
            self.info_label.config(text="Te pasaste. Pierdes.")
            self.end_game()

    def stand(self):
        """El jugador se planta y el dealer juega usando el árbol de probabilidad."""
        probability_tree = ArbolProbabilidad()
        
        while self.dealer_hand.value < 21:
            if probability_tree.should_hit(self.dealer_hand, self.player_hand.value, self.deck):
                self.dealer_hand.add_card(self.deck.deal_card())
                self.actualizar_Display()
            else:
                if self.dealer_hand.value < 17:
                    self.info_label.config(text="El dealer no tiene movimientos favorables. ¡Ganaste!")
                    self.balance += self.bet * 2
                    self.historial.add_historial(self.bet, "Ganaste", 
                                        [str(card) for card in self.player_hand.cards],
                                        [str(card) for card in self.dealer_hand.cards])
                    self.actualizar_Etiquetas()
                    self.end_game()
                    return
                break

        self.actualizar_Display()
        self.Resultados()
        
    def doblar_Apuesta(self):
        """El jugador dobla la apuesta y recibe una carta adicional."""
        if self.bet * 2 > self.balance:
            messagebox.showerror("Error", "No tienes suficientes Pecezuelos para doblar la apuesta.")
            return
        self.balance -= self.bet
        self.bet *= 2
        self.actualizar_Etiquetas()
        self.hit()
        if self.player_hand.value <= 21:
            self.stand()

    def Resultados(self):
        """Resuelve el juego comparando las manos del jugador y el dealer."""
        if self.dealer_hand.value > 21:
            self.info_label.config(text="El dealer se pasó. ¡Ganaste!")
            self.balance += self.bet * 2  # El jugador gana la apuesta
            result = "Ganaste"
        elif self.player_hand.value > 21:
            self.info_label.config(text="Te pasaste. El dealer gana.")
            result = "Perdiste"
        elif self.player_hand.value > self.dealer_hand.value:
            self.info_label.config(text="¡Ganaste!")
            self.balance += self.bet * 2  # El jugador gana la apuesta
            result = "Ganaste"
        elif self.player_hand.value < self.dealer_hand.value:
            self.info_label.config(text="El dealer gana.")
            result = "Perdiste"
        else:
            self.info_label.config(text="Es un empate.")
            result = "Empate"

        self.historial.add_historial(self.bet, result, [str(card) for card in self.player_hand.cards],
                                [str(card) for card in self.dealer_hand.cards])
        self.actualizar_Etiquetas()
        self.end_game()

    def end_game(self):
        """Finaliza el juego y restablece los botones."""
        self.hit_button.config(state=tk.DISABLED)
        self.stand_button.config(state=tk.DISABLED)
        self.double_button.config(state=tk.DISABLED)
        self.deal_button.config(state=tk.NORMAL)

        if self.balance <= 0:
            messagebox.showinfo("Fin del juego", "¡Te quedaste sin Pecezuelos!")
            self.root.quit()

    def actualizar_Display(self):
        """Actualiza la pantalla con las manos del jugador y el dealer."""
        self.mostrar_Mano(self.dealer_frame, self.dealer_hand)
        self.mostrar_Mano(self.player_frame, self.player_hand)

    def mostrar_Historial(self):
        """Muestra el historial del jugador."""
        top = Toplevel(self.root)
        top.title("Historial de Jugadas")
        top.geometry("600x400")
        
        historial_records = self.historial.get_Historial()
        
        if not historial_records:
            tk.Label(top, text="No hay historial de jugadas.", font=("Arial", 14)).pack(pady=20)
        else:
            for record in historial_records:
                record_text = f"Apuesta: {record['bet']} Pecezuelos | Resultado: {record['result']} | " \
                              f"Mano Jugador: {', '.join(record['player_hand'])} | Mano Dealer: {', '.join(record['dealer_hand'])}"
                tk.Label(top, text=record_text, font=("Arial", 12), anchor="w", padx=10).pack(fill="x", pady=5)

# main
if __name__ == "__main__":
    root = tk.Tk()
    app = Blackjack(root)
    root.mainloop()
