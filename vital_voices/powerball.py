import random

class PowerballSimulator:
    random.seed(41)
    def __init__(self):
        self.ticket_cost = 1.21  # Cost per ticket in dollars
        self.odds = {
            "Division 1": 134490400,
            "Division 2": 7078443,
            "Division 3": 686176,
            "Division 4": 36115,
            "Division 5": 16943,
            "Division 6": 1173,
            "Division 7": 892,
            "Division 8": 188,
            "Division 9": 66
        }
        self.prizes = {
            "Division 1": 10000000000,  # Jackpot (adjust as needed)
            "Division 2": 188606.60,
            "Division 3": 11008.65,
            "Division 4": 470.05,
            "Division 5": 166.70,
            "Division 6": 74.45,
            "Division 7": 42.90,
            "Division 8": 19.75,
            "Division 9": 11.95
        }

    def simulate_draw(self):
        return random.random()  # Generate a random float between 0 and 1

    def check_win(self, draw):
        cumulative_odds = 0
        for division, odds in self.odds.items():
            cumulative_odds += 1 / odds
            if draw <= cumulative_odds:
                return division
        return None

    def simulate_plays(self, num_tickets):
        total_cost = num_tickets * self.ticket_cost
        total_winnings = 0
        for _ in range(num_tickets):
            draw = self.simulate_draw()
            win = self.check_win(draw)
            if win:
                total_winnings += self.prizes[win]
        net_result = total_winnings - total_cost
        return net_result

def simulate_and_return_lists(max_tickets):
    simulator = PowerballSimulator()
    max_tickets = max_tickets  # Simulate up to 1000 tickets
    step = 10  # Increment by 10 tickets each time
    
    tickets = list(range(step, max_tickets + step, step))
    losses = []
    for num_tickets in tickets:
        net_result = simulator.simulate_plays(num_tickets)
        losses.append(-net_result)  # Convert net result to loss
    # Calculate and print the average loss per ticket
    avg_loss_per_ticket = losses[-1] / tickets[-1]
    # Calculate and print the expected return
    total_cost = tickets[-1] * simulator.ticket_cost
    total_winnings = total_cost - losses[-1]
    expected_return = (total_winnings / total_cost) * 100
  
    #loss =  100 - expected_return

    return tickets, losses,avg_loss_per_ticket
