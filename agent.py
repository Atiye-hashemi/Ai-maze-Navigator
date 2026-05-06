import random
from logic_engine import KnowledgeBase
from optimizer import run_ga

class RationalAgent:
    def __init__(self, start_pos, target_pos, maze_shape):
        self.pos = start_pos
        self.target = target_pos
        self.kb = KnowledgeBase(maze_rows=maze_shape[0], maze_cols=maze_shape[1])
        self.path_history = [start_pos]

    def think_and_act(self, maze_matrix):
        # 1. Ask for houses that have NOT been visited yet
        unvisited_safe = self.kb.infer_unvisited_safe_moves(self.pos)
        
        # 2. Get the Genetic Algorithm's best guess
        best_path = run_ga(maze_matrix, self.pos, self.target, self.kb)
        ga_move = best_path[0]
        ga_step = (self.pos[0] + ga_move[0], self.pos[1] + ga_move[1])

        # 3. Decision Logic: If a new house exists, do not revisit old ones
        if unvisited_safe:
            unvisited_coords = [move[1] for move in unvisited_safe]
            
            # If GA suggests a new house, follow it
            if ga_step in unvisited_coords:
                next_step = ga_step
            else:
                # Force exploration if GA suggests a loop
                _, next_step = random.choice(unvisited_safe)
        else:
            # Backtrack only if there are no unvisited houses nearby
            all_safe = self.kb.infer_safe_moves(self.pos)
            if all_safe:
                _, next_step = random.choice(all_safe)
            else:
                return False 

        # 4. Update position and memory
        self.pos = next_step
        self.kb.tell_visited(self.pos)
        self.path_history.append(self.pos)
        return True