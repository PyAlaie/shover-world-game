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
                if not is_box(map[i][j]):
                    continue
                
                extend = 1
                while is_perfect_square(map, (i,j), extend):
                    new_perf_sq = PerfectSquare((i,j), extend)
                    if new_perf_sq not in perviously_found_perfect_squares:
                        res.append(new_perf_sq)
                    
                    extend += 1
        
        return res
    
if __name__ == "__main__":
    sq1 = PerfectSquare((1,1), extend=3)
    sq2 = PerfectSquare((1,1), extend=3)

    print(sq1 == sq2)