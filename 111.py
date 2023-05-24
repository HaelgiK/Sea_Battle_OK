from random import randint
from time import sleep


class BoardException(Exception):
    pass


class OffBoardException(BoardException):
    def __str__(self):
        return "Выстрел сделан за пределы игрового поля!"


class OccupiedBoardException(BoardException):
    def __str__(self):
        return "В эти координаты уже стреляли!"


class WrongPositionShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'({self.x}, {self.y})'


class Ship:
    def __init__(self, bow_ship, length, orientation):
        self.bow_ship = bow_ship
        self.length = length
        self.orientation = orientation
        self.lives = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cur_position_x = self.bow_ship.x
            cur_position_y = self.bow_ship.y

            if self.orientation == 0:
                cur_position_x += i
            elif self.orientation == 1:
                cur_position_y += i

            ship_dots.append(Dot(cur_position_x, cur_position_y))

        return ship_dots

    def shooting(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hide=False, size=6):
        self.size = size
        self.hide = hide

        self.count = 0

        self.field = [["\033[33m \033[0m"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise WrongPositionShipException()

        for d in ship.dots:
            self.field[d.x][d.y] = "\033[33m■\033[0m"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, need=False):
        around = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in around:
                current = Dot(d.x + dx, d.y + dy)
                if not (self.out(current)) and current not in self.busy:
                    if need:
                        self.field[current.x][current.y] = "\033[34mo\033[0m"
                    self.busy.append(current)

    def __str__(self):
        field_result = ""
        field_result += "  | a | b | c | d | e | f | "
        for i, row in enumerate(self.field):
            field_result += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hide:
            field_result = field_result.replace("■", "\033[33m \033[0m")
        return field_result

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise OffBoardException()

        if d in self.busy:
            raise OccupiedBoardException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "\033[31mX\033[0m"
                if len(ship.dots) == 3:
                    if not self.hide:
                        print("\033[31mТрехпалубный флагман вашего флота атакован..!\033[0m")
                        sleep(1.5)
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, need=True)
                    print("Корабль потоплен!")
                    return True
                else:
                    print("Попадание в корабль!")
                    return True

        self.field[d.x][d.y] = "\033[34mo\033[0m"
        print(" Мимо!")
        return False

    def begin_game(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy_board):
        self.board = board
        self.enemy_board = enemy_board

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                shooting_target = self.ask()
                repeat_shooting = self.enemy_board.shot(shooting_target)
                return repeat_shooting
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход противника:⚔ {d.y + 1} {d.x + 1}")
        return d


class User(Player):
    def ask(self):
        x_index = " abcdef"
        while True:
            coordinates = input("Ваш ход:⚔ ").split()

            if len(coordinates) != 2:
                print("Введите 2 координаты через пробел! ")
                continue

            x, y = coordinates

            if x not in x_index:
                print("Координата по оси 'x' введена неверно!")
                continue

            if not (x.isalpha()) or not (y.isdigit()):
                print("Введите правильные координаты! ")
                continue

            x = x_index.index(x)
            x, y = int(x), int(y)

            return Dot(y-1, x-1)


class Game:
    def __init__(self, size=6):
        self.size = size

        player_board = self.random_board()
        enemy_board = self.random_board()
        enemy_board.hide = True

        self.ai = AI(enemy_board, player_board)
        self.us = User(player_board, enemy_board)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        list_ = [3, 2, 2, 1, 1, 1]
        board = Board(size=self.size)
        attempts_arrange = 0
        for length in list_:
            while True:
                attempts_arrange += 1
                if attempts_arrange > 100:
                    return None

                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), length, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except WrongPositionShipException:
                    pass

        board.begin_game()
        return board

    def before(self):
        print("%32s " % "\033[3m\033[1m\033[34m⚓ SEA ⚓\033[0m")
        sleep(1)
        print("%33s " % "\033[3m\033[1m\033[34mBATTLE\033[0m")
        sleep(1.5)
        print()
        print("\033[3mКоордината x - это буквы a,b,c,d,e,f ")
        sleep(1.5)
        print("Координата y - это цифры 1,2,3,4,5,6")
        sleep(1.5)
        print("Ввод координат - через пробел!\033[0m")
        print()

    def print_boards_user(self):
        print("-" * 27)
        print("%23s " % "Доска пользователя:")
        print(self.us.board)
        print("-" * 27)

    def print_boards_AI(self):
        print("%23s " % "Доска противника:")
        print(self.ai.board)
        print("-" * 27)

    def game_loop(self):
        move_number = 0
        while True:
            if move_number % 2 == 0:
                sleep(1)
                self.print_boards_AI()
                repeat = self.us.move()
            else:
                sleep(1)
                repeat = self.ai.move()
                self.print_boards_user()
            if repeat:
                sleep(1)
                move_number -= 1
            if self.ai.board.count == 6:
                self.print_boards_AI()
                print("\033[34mВы выиграли!\033[0m")
                break

            if self.us.board.count == 6:
                self.print_boards_user()
                print("\033[34mВы проиграли..!\033[0m")
                break
            move_number += 1

    def start_game(self):
        self.before()
        self.game_loop()


g = Game()
g.start_game()
