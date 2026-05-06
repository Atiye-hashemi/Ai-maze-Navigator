import random
from logic_engine import KnowledgeBase   
from optimizer import run_ga

class RationalAgent:
    def __init__(self, start_pos, target_pos, maze_shape):
        self.pos = start_pos
        self.target = target_pos
        self.kb = KnowledgeBase(maze_rows=maze_shape[0], maze_cols=maze_shape[1])  # no more yellow
        self.path_history = [start_pos]
        self.last_reason = ""

    def think_and_act(self, maze_matrix):
        
        self.last_reason = ""

        unvisited_safe = self.kb.infer_unvisited_safe_moves(self.pos)
        best_path = run_ga(maze_matrix, self.pos, self.target, self.kb)
        ga_move = best_path[0]
        ga_step = (self.pos[0] + ga_move[0], self.pos[1] + ga_move[1])

        if unvisited_safe:
            unvisited_coords = [move[1] for move in unvisited_safe]
            
            if ga_step in unvisited_coords:
                next_step = ga_step
                self.last_reason = "GA suggested an unvisited safe cell → followed GA"  
            else:
                _, next_step = random.choice(unvisited_safe)
                self.last_reason = "GA looped → forced exploration to random unvisited"  
        else:
            all_safe = self.kb.infer_safe_moves(self.pos)
            if all_safe:
                _, next_step = random.choice(all_safe)
                self.last_reason = "No unvisited cells → backtracking to safe neighbour"  
            else:
                self.last_reason = "STUCK — no safe moves available"                     
                return False

        self.pos = next_step
        self.kb.tell_visited(self.pos)
        self.path_history.append(self.pos)
        return True