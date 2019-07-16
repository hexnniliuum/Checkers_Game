from copy import deepcopy
import time

color = ["Black", "White"]
bSize = 8
pieces = 12


max_depth = 4

''' 0 - PvsAI
    1 - PvsP
    2 - AIvsAI'''
GMODE = 2

'''Alpha Beta on/off'''
ABSwitch = 1

timeB = []
timeW = []


class mmValue_copy:
    def __init__(self, val, move, max_depth, child_nodes, AB_max, AB_min):
        self.val = val
        self.move = move
        self.max_depth = max_depth
        self.nodes = child_nodes
        self.AB_max = AB_max
        self.AB_min = AB_min


class bState_copy:
    def __init__(self, bState, player_now, player_prev):
        self.board = bState
        self.player = player_now
        self.player_prev = player_prev


class Moves:
    def __init__(self, st_point, end_point, kill=False):
        self.st_point = st_point
        self.end_point = end_point
        self.kill = kill
        self.kill_stat = []

class Round:
    def __init__(self, player=0):
        self.board = Board()
        self.player = player
        self.turn = 0

    def round_exec(self):
        self.game_mode(GMODE)
        print("Game Over")
        result = self.count_result(self.board)
        print("Black points: " + str(result[0]))
        print("White points: " + str(result[1]))
        if (result[0] > result[1]):
            print("Black wins")
        elif (result[1] > result[0]):
            print("White wins")
        else:
            print("Tie")
        self.board.show_bState()

    def game_mode(self, mode):
        if(mode == 0):
            while not (self.endCheck(self.board)):
                self.board.show_bState()
                print("Turn: " + color[self.turn])
                if (self.turn == self.player):
                    pos_move = self.board.countPosMove(self.turn)
                    if (len(pos_move) > 0):
                        move = self.chooseMove(pos_move)
                        self.execMove(move)
                    else:
                        print("Blocked")
                else:
                    pos_move = self.board.countPosMove(self.turn)
                    print("Moves: ")
                    for i in range(len(pos_move)):
                        print(str(i + 1) + ": ", end='')
                        print(str(pos_move[i].st_point) + " -> " + str(pos_move[i].end_point))
                    if (len(pos_move) > 0):
                        if (len(pos_move) == 1):
                            best_move = pos_move[0]
                        else:
                            bState = bState_copy(self.board, self.turn, self.turn)
                            start = time.time()
                            best_move = self.minmax(bState)
                            timeW.append(time.time() - start)
                        self.execMove(best_move)
                        print("AI: (" + str(best_move.st_point) + " -> " + str(best_move.end_point) + ")")
                self.turn = 1 - self.turn
        elif(mode == 1):
            while not (self.endCheck(self.board)):
                self.board.show_bState()
                print("Turn: " + color[self.turn])

                pos_move = self.board.countPosMove(self.turn)
                if (len(pos_move) > 0):
                    move = self.chooseMove(pos_move)
                    self.execMove(move)
                else:
                    print("Blocked")
                self.turn = 1 - self.turn
        elif(mode == 2):
                while not (self.endCheck(self.board)):
                    self.board.show_bState()
                    print("Turn: " + color[self.turn])
                    pos_move = self.board.countPosMove(self.turn)
                    print("Moves: ")
                    for i in range(len(pos_move)):
                        print(str(i + 1) + ": ", end='')
                        print(str(pos_move[i].st_point) + " -> " + str(pos_move[i].end_point))
                    if (len(pos_move) > 0):
                        if (len(pos_move) == 1):
                            best_move = pos_move[0]
                        else:
                            state = bState_copy(self.board, self.turn, self.turn)
                            start = time.time()
                            best_move = self.minmax(state)
                            if self.turn == 0:
                                timeB.append(time.time() - start)
                            elif self.turn == 1:
                                timeW.append(time.time() - start)
                        self.execMove(best_move)
                        print("AI: (" + str(best_move.st_point) + " -> " + str(best_move.end_point) + ")")
                    self.turn = 1 - self.turn

    def execMove(self, move):
        self.board.bMove(move, self.turn)
        if move.kill:
            print("Killed " + str(len(move.kill_stat)) + " " + color[1 - self.turn] + " piece/s")

    def chooseMove(self, pos_move):
        move = -1
        while move not in range(len(pos_move)):
            print("Moves: ")
            for i in range(len(pos_move)):
                print(str(i + 1) + ": ", end='')
                print(str(pos_move[i].st_point) + " -> " + str(pos_move[i].end_point))
            user_move = input("Choose a move: ")
            move = -1 if (user_move == '') else (int(user_move) - 1)
            if move not in range(len(pos_move)):
                print("Choose again")
        return (pos_move[move])

    def endCheck(self, board):
        if (len(board.piece_pos_arr[0]) == 0 or len(board.piece_pos_arr[1]) == 0):
            return True
        elif (len(board.countPosMove(0)) == 0 and len(board.countPosMove(1)) == 0):
            return True
        else:
            return False

    def count_result(self, board):
        result = [0, 0]
        for cell in range(len(board.piece_pos_arr[0])):
            if (board.piece_pos_arr[0][cell][0] == 0):
                result[0] += 2
            else:
                result[0] += 1
        for cell in range(len(board.piece_pos_arr[1])):
            if (board.piece_pos_arr[1][cell][0] == bSize - 1):
                result[1] += 2
            else:
                result[1] += 1
        return result

    def minmax(self, bState):
        result = self.mm_max(bState, -999, 999, 0)
        return result.move

    def mm_max(self, state, alpha, beta, node):
        pos_move = state.board.countPosMove(state.player)
        curr_node = mmValue_copy(-999, None, node, 1, 0, 0)

        if (node == max_depth):
            curr_node.val = self.EvalFunc(state.board, state.player_prev)
            return curr_node

        if (len(pos_move) == 0):
            result = self.count_result(state.board)
            if (result[state.player_prev] > result[1 - state.player_prev]):
                curr_node.val = 100 + (2 * result[state.player_prev] - result[1 - state.player_prev])
            else:
                curr_node.val = -100 + (2 * result[state.player_prev] - result[1 - state.player_prev])
            return curr_node

        for act in pos_move:
            state_copy = bState_copy(deepcopy(state.board), 1 - state.player, state.player_prev)
            state_copy.board.bMove(act, state.player)
            curr_node_copy = self.mm_min(state_copy, alpha, beta, node + 1)

            if (curr_node_copy.max_depth > curr_node.max_depth):
                curr_node.max_depth = curr_node_copy.max_depth

            curr_node.nodes += curr_node_copy.nodes
            curr_node.AB_max += curr_node_copy.AB_max
            curr_node.AB_min += curr_node_copy.AB_min

            if (curr_node_copy.val > curr_node.val):
                curr_node.val = curr_node_copy.val
                curr_node.move = act

            if (ABSwitch == 1):
                if (curr_node.val >= beta):
                    curr_node.AB_max += 1
                    return curr_node
                if (curr_node.val > alpha):
                    alpha = curr_node.val

        return curr_node

    def mm_min(self, state, alpha, beta, node):
        pos_move = state.board.countPosMove(state.player)
        curr_node = mmValue_copy(999, None, node, 1, 0, 0)

        if (node == max_depth):
            curr_node.val = self.EvalFunc(state.board, state.player)
            return curr_node

        if (len(pos_move) == 0):
            result = self.count_result(state.board)
            if (result[state.player_prev] > result[1 - state.player_prev]):
                curr_node.val = 100 + (2 * result[state.player_prev] - result[1 - state.player_prev])
            else:
                curr_node.val = -100 + (2 * result[state.player_prev] - result[1 - state.player_prev])
            return curr_node

        for act in pos_move:
            state_copy = bState_copy(deepcopy(state.board), 1 - state.player, state.player_prev)
            state_copy.board.bMove(act, state.player)
            curr_node_copy = self.mm_max(state_copy, alpha, beta, node + 1)

            if (curr_node_copy.max_depth > curr_node.max_depth):
                curr_node.max_depth = curr_node_copy.max_depth

            curr_node.nodes += curr_node_copy.nodes
            curr_node.AB_max += curr_node_copy.AB_max
            curr_node.AB_min += curr_node_copy.AB_min

            if (curr_node_copy.val < curr_node.val):
                curr_node.val = curr_node_copy.val
                curr_node.move = act

            if (ABSwitch == 1):
                if (curr_node.val <= alpha):
                    curr_node.AB_min += 1
                    return curr_node
                if (curr_node.val < beta):
                    beta = curr_node.val

        return curr_node


    def EvalFunc(self, board, player_now):
        #EvalFunc 1.
        '''
        b_end, b_home, b_enemy = 0, 0, 0
        w_end, w_home, w_enemy = 0, 0, 0
        for i in range(len(board.piece_pos_arr[0])):
            if (board.piece_pos_arr[0][i][0] == bSize - 1):
                b_end += 1
            elif (bSize / 2 <= board.piece_pos_arr[0][i][0] < bSize):
                b_enemy += 1
            else:
                b_home += 1

        for i in range(len(board.piece_pos_arr[1])):
            if (board.piece_pos_arr[1][i][0] == 0):
                w_end += 1
            elif (0 <= board.piece_pos_arr[1][i][0] < bSize / 2):
                w_enemy += 1
            else:
                w_home += 1

        w_score = (3 * w_end) + (2 * w_enemy) + (1 * w_home)
        b_score = (3 * b_end) + (2 * b_enemy) + (1 * b_home)
        if (player_now == 0):
            return (b_score - w_score)
        else:
            return (w_score - b_score)

        '''

        #EvalFunc 2.
        if (self.endCheck(self.board)):
            fscore = self.count_result(self.board)
            if player_now == 0:
                if fscore[0] > fscore[1]:
                    return float(999)
                if fscore[1] > fscore[0]:
                    return float(-999)
            elif player_now == 1:
                if fscore[0] < fscore[1]:
                    return float(999)
                if fscore[1] < fscore[0]:
                    return float(-999)
            if fscore[1] == fscore[0]:
                return 0

        if (len(board.piece_pos_arr[player_now])==0) | (len(board.piece_pos_arr[player_now])==1):
                return 0

        #modifier: -1 gives advantage
        if (player_now == 1):
            pieces = board.piece_pos_arr[1]
            modifier = -1
        else:
            pieces = board.piece_pos_arr[0]
            modifier = 1

        dist = 0
        for piece1 in pieces:
            for piece2 in pieces:
                if piece1 == piece2:
                    continue
                dist_y = abs(piece1[0] - piece2[0])
                dist_x = abs(piece1[1] - piece2[1])
                dist += dist_x ** 2 + dist_y ** 2
        dist /= len(pieces)
        return (1.0 / dist * modifier)


class Board:
    def __init__(self, board=[], pos_b=[], w_pos=[]):
        if (board != []):
            self.bState = board
        else:
            self.showStartBoard()
        self.piece_pos_arr = [[], []]

        if (pos_b != []):
            self.piece_pos_arr[0] = pos_b
        else:
            self.piece_pos_arr[0] = self.findPieces(0)

        if (w_pos != []):
            self.piece_pos_arr[1] = w_pos
        else:
            self.piece_pos_arr[1] = self.findPieces(1)

    def bMove(self, move_points, player_now):
        move = [move_points.st_point, move_points.end_point]

        kill = move_points.kill
        self.bState[move[0][0]][move[0][1]] = -1
        self.bState[move[1][0]][move[1][1]] = player_now
        if kill:
            for enemy in move_points.kill_stat:
                self.bState[enemy[0]][enemy[1]] = -1
        if kill:
            self.piece_pos_arr[0] = self.findPieces(0)
            self.piece_pos_arr[1] = self.findPieces(1)
        else:
            self.piece_pos_arr[player_now].remove((move[0][0], move[0][1]))
            self.piece_pos_arr[player_now].append((move[1][0], move[1][1]))


    def countPosMove(self, player):
        possible_moves = []
        kill_pos = False

        next = -1 if player == 0 else 1
        bEnd = 0 if player == 0 else bSize - 1

        for cell in self.piece_pos_arr[player]:
            if (cell[0] == bEnd):
                continue
            if (cell[1] != bSize - 1):
                if (self.bState[cell[0] + next][cell[1] + 1] == -1 ):
                    move_copy = Moves((cell[0], cell[1]), (cell[0] + next, cell[1] + 1))
                    possible_moves.append(move_copy)
                elif (self.bState[cell[0] + next][cell[1] + 1] == 1 - player):
                    kills = self.JumpTest((cell[0], cell[1]), False, player)
                    if (len(kills) != 0):
                        if not kill_pos:
                            kill_pos = True
                        possible_moves.extend(kills)

            if (cell[1] != 0):
                if (self.bState[cell[0] + next][cell[1] - 1] == -1 ):
                    move_copy = Moves((cell[0], cell[1]), (cell[0] + next, cell[1] - 1))
                    possible_moves.append(move_copy)
                elif (self.bState[cell[0] + next][cell[1] - 1] == 1 - player):
                    kills = self.JumpTest((cell[0], cell[1]), True, player)
                    if (len(kills) != 0):
                        if not kill_pos:
                            kill_pos = True
                        possible_moves.extend(kills)

        return possible_moves

    def JumpTest(self, cell, pleft, player):
        kills = []
        next = -1 if player == 0 else 1

        if (cell[0] + next == 0 or cell[0] + next == bSize - 1):
            return kills

        if (pleft):
            if (cell[1] > 1 and self.bState[cell[0] + next + next][cell[1] - 2] == -1):
                move_copy = Moves(cell, (cell[0] + next + next, cell[1] - 2), True)
                move_copy.kill_stat = [(cell[0] + next, cell[1] - 1)]

                if (move_copy.end_point[0] + next > 0 and move_copy.end_point[0] + next < bSize - 1):

                    if (move_copy.end_point[1] > 1 and self.bState[move_copy.end_point[0] + next][move_copy.end_point[1] - 1] == (1 - player)):
                        blind_jump = self.JumpTest(move_copy.end_point, True, player)
                        if (blind_jump != []):
                            move_ccopy = deepcopy(move_copy)
                            move_ccopy.end_point = blind_jump[0].end_point
                            move_ccopy.kill_stat.extend(blind_jump[0].kill_stat)
                            kills.append(move_ccopy)

                    if (move_copy.end_point[1] < bSize - 2 and self.bState[move_copy.end_point[0] + next][move_copy.end_point[1] + 1] == (1 - player)):
                        blind_jump = self.JumpTest(move_copy.end_point, False, player)
                        if (blind_jump != []):
                            move_ccopy = deepcopy(move_copy)
                            move_ccopy.end_point = blind_jump[0].end_point
                            move_ccopy.kill_stat.extend(blind_jump[0].kill_stat)
                            kills.append(move_ccopy)
                kills.append(move_copy)
        else:
            if (cell[1] < bSize - 2 and self.bState[cell[0] + next + next][cell[1] + 2] == -1):
                move_copy = Moves(cell, (cell[0] + next + next, cell[1] + 2), True)
                move_copy.kill_stat = [(cell[0] + next, cell[1] + 1)]

                if (move_copy.end_point[0] + next > 0 and move_copy.end_point[0] + next < bSize - 1):

                    if (move_copy.end_point[1] > 1 and self.bState[move_copy.end_point[0] + next][move_copy.end_point[1] - 1] == (1 - player)):
                        blind_jump = self.JumpTest(move_copy.end_point, True, player)
                        if (blind_jump != []):
                            move_ccopy = deepcopy(move_copy)
                            move_ccopy.end_point = blind_jump[0].end_point
                            move_ccopy.kill_stat.extend(blind_jump[0].kill_stat)
                            kills.append(move_ccopy)

                    if (move_copy.end_point[1] < bSize - 2 and self.bState[move_copy.end_point[0] + next][move_copy.end_point[1] + 1] == (1 - player)):
                        blind_jump = self.JumpTest(move_copy.end_point, False, player)
                        if (blind_jump != []):
                            move_ccopy = deepcopy(move_copy)
                            move_ccopy.end_point = blind_jump[0].end_point
                            move_ccopy.kill_stat.extend(blind_jump[0].kill_stat)
                            kills.append(move_ccopy)
                kills.append(move_copy)

        return kills

    def findPieces(self, player):
        position = []
        for row in range(bSize):
            for col in range(bSize):
                if (self.bState[row][col] == player):
                    position.append((row, col))
        return position

    def show_bState(self):
        for col in range(bSize):
            print(str(col) + " ", end='')
        print("")
        for row in range(bSize):
            for col in range(bSize):
                if (self.bState[row][col] == -1):
                    print("* ", end='')
                elif (self.bState[row][col] == 1):
                    print("@ ", end='')
                elif (self.bState[row][col] == 0):
                    print("0 ", end='')
            print(str(row))

    def showStartBoard(self):
        self.bState = [
            [-1, 1, -1, 1, -1, 1, -1, 1],
            [1, -1, 1, -1, 1, -1, 1, -1],
            [-1, 1, -1, 1, -1, 1, -1, 1],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [0, -1, 0, -1, 0, -1, 0, -1],
            [-1, 0, -1, 0, -1, 0, -1, 0],
            [0, -1, 0, -1, 0, -1, 0, -1]
        ]


def main():

    player = 0
    game = Round(player)
    game.round_exec()

    if GMODE == 2:
        print(sum(timeB) / len(timeB))
    print(sum(timeW) / len(timeW))


main()