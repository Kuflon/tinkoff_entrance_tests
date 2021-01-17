import numpy as np
import copy
import pickle

np.random.seed(49)


class Solver:
    """
    I took a ready-made solver, because I didn't have enough time
    ref:
    http://itnotesblog.ru/note.php?id=157
    """

    def solve(self, puzzle):
        solution = copy.deepcopy( puzzle )
        if self.solveHelper( solution ):
            return solution
        return None

    def solveHelper(self, solution):
        minPossibleValueCountCell = None
        while True:
            minPossibleValueCountCell = None
            for rowIndex in range( 9 ):
                for columnIndex in range( 9 ):
                    if solution[ rowIndex ][ columnIndex ] != 0:
                        continue
                    possibleValues = self.findPossibleValues( rowIndex, columnIndex, solution )
                    possibleValueCount = len( possibleValues )
                    if possibleValueCount == 0:
                        return False
                    if possibleValueCount == 1:
                        solution[ rowIndex ][ columnIndex ] = possibleValues.pop()
                    if not minPossibleValueCountCell or \
                       possibleValueCount < len( minPossibleValueCountCell[ 1 ] ):
                        minPossibleValueCountCell = ( ( rowIndex, columnIndex ), possibleValues )
            if not minPossibleValueCountCell:
                return True
            elif 1 < len( minPossibleValueCountCell[ 1 ] ):
                break
        r, c = minPossibleValueCountCell[ 0 ]
        for v in minPossibleValueCountCell[ 1 ]:
            solutionCopy = copy.deepcopy( solution )
            solutionCopy[ r ][ c ] = v
            if self.solveHelper( solutionCopy ):
                for r in range( 9 ):
                    for c in range( 9 ):
                        solution[ r ][ c ] = solutionCopy[ r ][ c ]
                return True
        return False

    def findPossibleValues(self, rowIndex, columnIndex, puzzle ):
        values = { v for v in range( 1, 10 ) }
        values -= self.getRowValues( rowIndex, puzzle )
        values -= self.getColumnValues( columnIndex, puzzle )
        values -= self.getBlockValues( rowIndex, columnIndex, puzzle )
        return values

    def getRowValues(self, rowIndex, puzzle ):
        return set( puzzle[ rowIndex ][ : ] )

    def getColumnValues(self, columnIndex, puzzle ):
        return { puzzle[ r ][ columnIndex ] for r in range( 9 ) }

    def getBlockValues(self, rowIndex, columnIndex, puzzle ):
        blockRowStart = 3 * ( rowIndex // 3 )
        blockColumnStart = 3 * ( columnIndex // 3 )
        return {
            puzzle[ blockRowStart + r ][ blockColumnStart + c ]
                for r in range( 3 )
                for c in range( 3 )
        }


class Grid(Solver):

    def __init__(self):
        self.n = 3
        self._table = np.array([[(int((i*self.n + i/self.n + j) % (self.n*self.n) + 1)) for j in range(self.n*self.n)] for i in range(self.n*self.n)])


    def shuffle(self, times=3):

        for i in range(times):
            #transpose
            self._table = self._table.T

            self._swap_row_areas()

            #swap columns areas
            self._table = self._table.T
            self._swap_row_areas()
            self._table = self._table.T


    def _swap_row_areas(self):

        first_area_idx = np.random.randint(0, self.n)
        second_area_idx = np.random.randint(0, self.n)

        while(first_area_idx == second_area_idx):
            second_area_idx = np.random.randint(0, self.n)

        for i in range(self.n):
            ind1, ind2 = first_area_idx*self.n + i, second_area_idx*self.n + i
            bottle1, bottle2 = copy.deepcopy(self._table[ind1]), copy.deepcopy(self._table[ind2])
            self._table[ind1], self._table[ind2] = bottle2, bottle1


    def clear_cells(self, cell_fills):

        visited = [[0 for j in range(self.n*self.n)] for i in range(self.n*self.n)]

        for i in range(self.n ** 4 - cell_fills):

            i_tbl, j_tbl, cur_val = self._clear_random_cell(visited)


            while self.solve(self._table) is None:
                self._table[i_tbl][j_tbl] = cur_val

                i_tbl, j_tbl, cur_val = self._clear_random_cell(visited)


    def _clear_random_cell(self,visited):

        i,j = np.random.randint(0, self.n*self.n), np.random.randint(0, self.n*self.n)

        while(visited[i][j] == 1):
            i,j = np.random.randint(0, self.n*self.n), np.random.randint(0, self.n*self.n)

        visited[i][j] = 1

        cur_val = self._table[i][j]
        self._table[i][j] = 0

        return i, j, cur_val


    def get_table(self):
        return self._table


    def show(self):
        print('The base table:')
        for i in range(self.n*self.n):
            print(self._table[i])


class Controller(Solver):

    def __init__(self):
        self.clear_table = None
        self.answer_table = None


    def get_commands(self):
        commands = {
            'save':'self.save_pkl()',
            'load':'self.load_pkl()',
            'exit':'self.main_menu()',
            'help':'self.show_commands_list()'
        }

        return commands


    def save_pkl(self):
        with open('answer_table.pkl', 'wb') as f1:
            pickle.dump(self.answer_table, f1)
        with open('clear_table.pkl', 'wb') as f2:
            pickle.dump(self.clear_table, f2)


        print("\nУспешно сохранено!\n")


    def load_pkl(self):
        with open('answer_table.pkl', 'rb') as f1:
            self.answer_table = pickle.load(f1)
        with open('clear_table.pkl', 'rb') as f2:
            self.clear_table = pickle.load(f2)

        print("\nУспешно загружена последняя игра!\n")
        self.print_grid(self.clear_table)



    def show_commands_list(self):
        print("Список команд:\n\
        save - сохранить текущую игру\n\
        load - загрузить последнюю игру\n\
        exit - выйти в главное меню")


    def print_grid(self, grid):

        print("---------------------------")

        for i in range(3*3):

            print(grid[i][:3], "|", grid[i][3:6], "|", grid[i][6:9])

            if (i+1) % 3 == 0:
                print("---------------------------")


    def main_menu(self):

        print('Sudoku game\n')

        commands = self.get_commands()

        print('Режимы игры:\n1.Пользователь vs Sudoku\n2.PC vs Sudoku\n')
        status = False

        while status is False:
            choice = input("Введите 1 или 2: ")

            if choice == "1":
                status = True

                self.start_mode_1()

            elif choice == "2":
                status = True

                self.start_mode_2()

            elif choice == "help":
                eval(choice)

            else:
                print("Введите верную команду, или help для просмотра списка команд")


    def start_mode_2(self):

        grid = Grid()
        grid.shuffle(times=3)
        self.answer_table = grid.get_table()

        cell_fills = int(input("Введите количество заполненных клеточек < 81: ")) # max = 81
        grid.clear_cells(cell_fills)
        self.clear_table = grid.get_table()
        self.print_grid(self.clear_table)

        solution = self.solve(self.clear_table)
        print("Done, human")
        self.print_grid(solution)

        self.main_menu()


    def start_mode_1(self):

        grid = Grid()
        grid.shuffle(times=3)
        self.answer_table = copy.deepcopy(grid.get_table())

        cell_fills = int(input("Введите количество заполненных клеточек < 81: ")) # max = 81
        grid.clear_cells(cell_fills)
        self.clear_table = grid.get_table()

        print("Игра началась:")
        print("Ваш ответ: №строки№колонкиЦифра    нумерация с 1")
        self.print_grid(self.clear_table)

        game_status = True

        while game_status is True:

            ans = input("Ход или команда:")

            if ans in self.get_commands():
                eval(self.get_commands()[ans])
                continue

            i, j, val = int(ans[0])-1, int(ans[1])-1, int(ans[2])

            if self.answer_table[i][j] == val:
                self.clear_table[i][j] = val
            else:
                print("Неверный ход")
                continue

            if (self.answer_table==self.clear_table).all():
                game_status = False
                print("Грац, ты выиграл!")
                self.print_grid(self.clear_table)
                self.main_menu()

            self.print_grid(self.clear_table)


def main():
    Controller().main_menu()


if __name__ == "__main__":
    main()
