from math import sqrt
from time import time
from typing import Iterable
from abc import ABC , abstractmethod
from numpy import array_str , all , array
from collections import deque
import heapq
class SearchAgent(ABC):

    frontier : Iterable
    states = set() #explored states
    keys = ((0,-1),(0,1),(-1,0),(1,0))
    goal = array([[0,1,2],[3,4,5],[6,7,8]])

    def __init__(self,state,init) -> None:
        super().__init__()
        self.state = state
        self.frontier = init([])

    @abstractmethod
    def search(self):
        pass

    class Results:

        def __init__(self,moves: list,found: bool,states: int) -> None:
            self.moves = moves
            self.found = found
            self.states = states

def timer(f):
    ts = time()
    res = f()
    return time()-ts , res
class DFS(SearchAgent):

    def __init__(self,state) -> None:
        super().__init__(state,deque)

    def search(self):
        self.frontier.append(self.state)
        while self.frontier :
            print(len(SearchAgent.states))
            state = self.frontier.pop()
            SearchAgent.states.add(array_str(state.grid))
            if state.checkWin():
                return SearchAgent.Results(state.backtrack(),True,len(SearchAgent.states))
            neighbours = state.true_neighbours()
            neighbours.reverse()
            for neighbour in neighbours:
                if neighbour not in self.frontier:
                    self.frontier.append(neighbour)
        return SearchAgent.Results([self.state.blank],False,0)

class BFS(SearchAgent):

    def __init__(self,state) -> None:
        super().__init__(state,deque)

    def search(self):        
        self.frontier.append(self.state)
        while self.frontier :
            print(len(SearchAgent.states))
            state = self.frontier.popleft()
            SearchAgent.states.add(array_str(state.grid))
            if state.checkWin():
                return SearchAgent.Results(state.backtrack(),True,len(SearchAgent.states))

            for neighbour in state.true_neighbours():
                if neighbour not in self.frontier:
                    self.frontier.append(neighbour)
        return SearchAgent.Results([self.state.blank],False,0)

class AStar(SearchAgent):

    def __init__(self,state) -> None:
        super().__init__(state,list)

    def search(self,type):
        self.state.cost = 0
        heapq.heappush(self.frontier,self.state)
        while self.frontier:
            print(len(SearchAgent.states))
            state = heapq.heappop(self.frontier)
            SearchAgent.states.add(array_str(state.grid))
            if state.checkWin():
                return SearchAgent.Results(state.backtrack(),True,len(SearchAgent.states))

            for neighbour in state.true_neighbours():
                neighbour.cost = self.state.cost + 1 + self.heu(neighbour,type)
                if neighbour not in self.frontier:
                    heapq.heappush(self.frontier,neighbour)
                else:
                    self.decreaseKey(state,neighbour.cost,self.frontier.index(neighbour))
        return SearchAgent.Results([self.state.blank],False,0)


    def heu(self,state,type):
        """
        calculates heuristics for a given state
        """
        sum = 0
        if type == 1:
            for i in range(3):
                for j in range(3):
                    num = state.grid[i][j]
                    if num == 0:
                        continue
                    x = (num%3) - j
                    y = (num//3) - i
                    sum += abs(x) + abs(y)
        else:
            for i in range(3):
                for j in range(3):
                    num = state.grid[i][j]
                    if num == 0:
                        continue
                    x = (num%3) - j
                    y = (num//3) - i
                    sum += sqrt((x**2) + (y**2))
        return sum

    def decreaseKey(self,parent,cost: int,index: int):
        state = self.frontier[index]
        if state.cost > cost:
            state.cost = cost
            state.parent = parent

class Node:
    def __init__(self, grid, parent, blank:tuple):
        self.grid = grid
        self.blank = blank
        self.parent = parent

class State:
    """
    Stores all data relevant to a specific grid state to facilitate searching
    """

    def __init__(self, grid ,parent ,blank: tuple) -> None:
        self.grid = grid
        self.parent = parent
        self.blank = blank

    def __lt__(self,other):
        return self.cost < other.cost 

    def true_neighbours(self) -> list:
        aval_states = []
        for num in self.availableStates():
            state = self.switchState(num)
            if not state.isExplored():
                aval_states.append(state)
        return aval_states

    def isExplored(self) -> bool:
        """
        checks if this state was already explored
        """
        hash = array_str(self.grid)
        return hash in SearchAgent.states

    def availableStates(self , keys = None):
        i = 1
        key = keys
        if keys is None:
            keys = SearchAgent.keys
            i = 4
            key = keys[0]
        aval_nums = []
        blank = self.blank
        for c in range(i):
            num = ((blank[0]+key[0]),(blank[1]+key[1]))
            if -1 < num[0] < 3 and -1 < num[1] < 3 :
                aval_nums.append(num)
            key = keys[(c % 3)+1]

        if len(aval_nums) < 2:
            return bool(aval_nums)
        return aval_nums

    def switchState(self,num: tuple):    
        l = self.grid.copy()
        blank = self.blank
        l[blank] , l[num] = l[num] , l[blank]
        return State(l,self,num)

    def checkWin(self):
        return (self.grid == SearchAgent.goal).all()

    def backtrack(self):
        st = self
        moves = [st.blank]
        while st.parent is not None:
            st = st.parent
            moves.append(st.blank)
        moves.reverse()
        return moves



def getInvCount(arr):
    inv_count = 0
    empty_value = 0
    for i in range(0, 9):
        for j in range(i + 1, 9):
            if arr[j] != empty_value and arr[i] != empty_value and arr[i] > arr[j]:
                inv_count += 1
    return inv_count

def isSolvable(puzzle) :
    inv_count = getInvCount([j for sub in puzzle for j in sub])
    return (inv_count % 2 == 0)
