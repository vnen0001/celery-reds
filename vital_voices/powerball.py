import random

class PowerballSimulator:
    def __init__(self, seed=41):
        random.seed(seed)  # Set the seed here
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
        main_numbers = random.sample(range(1, 36), 7)
        powerball = random.randint(1, 20)
        return main_numbers, powerball

    def check_win(self, main_numbers, powerball, ticket_main, ticket_powerball):
        matched_main = len(set(main_numbers) & set(ticket_main))
        matched_powerball = (powerball == ticket_powerball)
        
        # Determine division
        if matched_main == 7 and matched_powerball:
            return "Division 1"
        elif matched_main == 7:
            return "Division 2"
        elif matched_main == 6 and matched_powerball:
            return "Division 3"
        elif matched_main == 6:
            return "Division 4"
        elif matched_main == 5 and matched_powerball:
            return "Division 5"
        elif matched_main == 5:
            return "Division 6"
        elif matched_main == 4 and matched_powerball:
            return "Division 7"
        elif matched_main == 3 and matched_powerball:
            return "Division 8"
        elif matched_main == 2 and matched_powerball:
            return "Division 9"
        return None

    def simulate_plays(self, num_tickets):
        total_cost = num_tickets * self.ticket_cost
        total_winnings = 0
        for _ in range(num_tickets):
            main_numbers, powerball = self.simulate_draw()
            ticket_main = random.sample(range(1, 36), 7)
            ticket_powerball = random.randint(1, 20)
            win = self.check_win(main_numbers, powerball, ticket_main, ticket_powerball)
            if win:
                total_winnings += self.prizes[win]
        net_result = total_winnings - total_cost
        return net_result, total_cost

def simulate_and_return_lists(max_tickets):
    simulator = PowerballSimulator()  # Seed is set in the class
    step = 1  # Increment by 10 tickets each time
    
    tickets = list(range(step, max_tickets + step, step))
    cumulative_losses = []
    cumulative_investments = []
    
    total_loss = 0
    total_investment = 0
    
    for num_tickets in tickets:
        net_result, total_cost = simulator.simulate_plays(num_tickets)
        
        # Update cumulative investment and loss
        total_investment += total_cost
        total_loss += -net_result
        
        cumulative_investments.append(total_investment)
        cumulative_losses.append(total_loss)
        
    avg_loss_per_ticket = total_loss / tickets[-1]
    
    return tickets, cumulative_losses, cumulative_investments, avg_loss_per_ticket
