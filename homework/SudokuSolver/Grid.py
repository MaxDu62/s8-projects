from Case import *
from Solver import *

class Grille():

    solver_heuristique = 0
    blocked = 0
    
    MIN_FOR_BLOCKED = SolverUtils.SOLVER_SIZE + 2

    def __init__(self, grid):

        self.grid = list()

        if type(grid[0]) == list:
            grid = [x for x in l for l in grid]

        self.grid = map(lambda x: Case(x), grid)
        
    def __str__(self):
        tmp = ""
        for i in range(9):
            for j in range(9):
                tmp += self.grid[i * 9 + j].__str__()
                tmp += " "
            tmp += "\n"
        return tmp

    def get(self, pos=None, posy=None, instance_object=True):

        if pos == None:
            return self.grid
        elif posy != None:
            cell = self.grid[pos * 9 + posy]
            return cell if instance_object else cell.get()
        elif type(pos) == list:
            grid = [self.get(x) for x in pos]
            return grid if instance_object else map(lambda x : x.get(), grid)
        else:
            cell = self.grid[pos]
            return cell if instance_object else cell.get()

        return None

    def solve_find_cell_possible(self):

        solved_something = False
        solver_state = SolverUtils.solver_state(self.solver_heuristique)
        if solver_state == SolverUtils.SOLVE:
            for posy in range(9):
                for posx in range(9):
                    if self.get(posx, posy).is_tmp() or self.get(posx, posy).is_none():
                        possible = Solver.find_cell_possible(self, posx, posy)
                        self.get(posx, posy).notify(possible)

        elif solver_state == SolverUtils.GRID_REDUCE:
            for posy in range(0,9,3):
                for posx in range(0,9,3):
                    solved_something = Reducter.grid_elements(self, posx, posy)
        
        else:
            for pos in range(9):
                if solver_state == SolverUtils.HORIZONTAL_REDUCE:
                    solved_something = Reducter.horizontal_elements(self, pos)
                elif solver_state == SolverUtils.VERTICAL_REDUCE:
                    solved_something = Reducter.vertical_elements(self, pos)

        self.solver_heuristique = ( self.solver_heuristique + 1 ) % SolverUtils.SOLVER_SIZE
        self.blocked = self.blocked + 1 if not solved_something else 0
        
        if self.blocked == self.MIN_FOR_BLOCKED:
            print("Solver is blocked, need stronger heuristique")

    def validation(self):
        return len( filter(lambda x : x.is_constante(), self.grid) ) == len(self.grid) and  Validator.validation(grid=self)

    def getState(self):
        return SolverUtils.solver_state(self.solver_heuristique)
