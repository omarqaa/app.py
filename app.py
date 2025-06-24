import random

def simulate_crash_105_losses(num_simulations=100000):
    loss_threshold = 1.05
    consecutive_loss_counts = {2: 0, 3: 0, 4: 0, 5: 0}
    total_sequences = 0

    def generate_crash():
        r = random.random()
        return 1 / (1 - r)

    i = 0
    while i < num_simulations:
        loss_streak = 0
        while True:
            crash = generate_crash()
            if crash < loss_threshold:
                loss_streak += 1
                i += 1
                if i >= num_simulations:
                    break
            else:
                break

        if loss_streak >= 2:
            consecutive_loss_counts[2] += 1
        if loss_streak >= 3:
            consecutive_loss_counts[3] += 1
        if loss_streak >= 4:
            consecutive_loss_counts[4] += 1
        if loss_streak >= 5:
            consecutive_loss_counts[5] += 1

        total_sequences += 1

    results = {
        f"{k} خسائر متتالية": round(v / total_sequences * 100, 2)
        for k, v in consecutive_loss_counts.items()
    }
    return results

simulate_crash_105_losses(100000)
