from z3 import *

symbols = ['n', 'x', 'y']

for s in symbols:
    exec("%s = Int('%s')" % (s, s))
# 変数定義

equation = 'Or(n == x + y, And(x > 0, y > 0))'
# 基本制約
s = Solver()
s.add(eval(equation))

# 解を探索
while(s.check() == sat):
    # 解の表示
    m = s.model()
    print(m)
    
    # 解を制約条件に追加
    s.add(Not(n == m[n]))
