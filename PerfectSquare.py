from enums import Objects, is_box, is_perfect_square

class PerfectSquare:
    def __init__(self, start, extend):
        start_i, start_j = start

        self.start = start
        self.start_i = start_i
        self.start_j = start_j
        self.extend = extend

        self.age = 0

    def includes(self, position) -> bool:
        i,j = position

        if self.start_i <= i <= self.start_i + self.extend and self.start_j <= j <= self.start_j + self.extend:
            return True
        
        return False

    def exeeded_max_age(self, max_age):
        if self.age >= max_age:
            return True
        return False
    
    def increase_age(self):
        self.age += 1

    def dissolute(self, map):
        start_i, start_j = self.start
        for i in range(1,self.extend):
            for j in range(1,self.extend):
                map[start_i + i][start_j + j] = Objects.Empty.value
        return map

    def apply_barrier_maker(self, map):
        start_i, start_j = self.start
        for i in range(1,self.extend-1):
            for j in range(1,self.extend-1):
                map[start_i + i][start_j + j] = Objects.Barrier.value
        return map
    
    def apply_hellify(self, map):
        start_i, start_j = self.start

        for i in range(1, self.extend-1):
            map[start_i + i][start_j + 1] = Objects.Empty.value
            map[start_i + i][start_j + self.extend-2] = Objects.Empty.value
            map[start_i + 1][start_j + i] = Objects.Empty.value
            map[start_i + self.extend-2][start_j + i] = Objects.Empty.value
        
        for i in range(2,self.extend-2):
            for j in range(2,self.extend-2):
                map[start_i + i][start_j + j] = Objects.Lava.value
        return map

    def __eq__(self, value):
        if isinstance(value, PerfectSquare) and self.start == value.start and self.extend == value.extend:
            return True
        return False

    def __repr__(self):
        return f"start={self.start}|extend={self.extend}"

    def find_new_perfect_squares(map:list[list], perviously_found_perfect_squares:list) -> list:
        res = []

        n = len(map)
        m = len(map[0])
        for i in range(n):
            for j in range(m):
                extend = 4
                while i + extend <= n and j + extend <= m:
                    if is_perfect_square(map, (i,j), extend):
                        new_perf_sq = PerfectSquare((i,j), extend)
                        if new_perf_sq not in perviously_found_perfect_squares:
                            res.append(new_perf_sq)
                        
                        break
                    
                    extend += 1
        
        return res
    
if __name__ == "__main__":
    sq1 = PerfectSquare((1,1), extend=3)
    sq2 = PerfectSquare((1,1), extend=3)

    print(sq1 == sq2)