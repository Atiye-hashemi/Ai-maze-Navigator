import random
from math_utils import get_l1_norm

MOVES = [(0, 1), (1, 0), (-1, 0), (0, -1)]

def fitness(path, start, target, kb):
    r, c = start
    penalty = 0
    for move in path:
        nr, nc = r + move[0], c + move[1]
        if not kb.is_safe((nr, nc)):
            return float('inf')
        if kb.is_visited((nr, nc)):
            penalty += 5000  # High penalty for revisiting squares
        r, c = nr, nc
    
    # Fitness is distance to target + any revisiting penalties
    return get_l1_norm((r, c), target) + penalty

def run_ga(maze, start_pos, target_pos, kb):
    pop_size = 40
    generations = 50
    # Create initial random paths
    population = [[random.choice(MOVES) for _ in range(10)] for _ in range(pop_size)]

    for _ in range(generations):
        # Score the population
        scored = []
        for p in population:
            score = fitness(p, start_pos, target_pos, kb)
            scored.append((score, p))
        
        scored.sort(key=lambda x: x[0])
        
        # Selection: Keep the best 50%
        selected = [p for _, p in scored[:pop_size // 2]]
        
        # Reproduction
        new_population = selected.copy()
        while len(new_population) < pop_size:
            p1, p2 = random.sample(selected, 2)
            cut = random.randint(1, 8)
            child = p1[:cut] + p2[cut:]
            
            # Mutation
            if random.random() < 0.2:
                child[random.randint(0, 9)] = random.choice(MOVES)
            
            new_population.append(child)
        population = new_population

    # Return the single best move sequence found
    return scored[0][1]