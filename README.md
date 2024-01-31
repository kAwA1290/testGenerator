## testGenerator
Pythonコードをシンボリック実行により静的解析し、コード内のすべてのIfブロックに対するテストケースを生成するプログラムです。
シンボリック実行によってIfブロックへの到達制約をSMT問題に落としこみ、SMTソルバによるテストケースの生成を行っています。
### 実行例
以下のように簡単なプログラムを入力します。
```
if __name__ == "__main__":
    sample = """
if a > 0:
    if b < 2 & c > 3:
        pass
        if d == 2:
            if e == 2:
                pass
        if e == 2:
            pass
        if f == 2:
            pass
"""
```
テスト例が生成されました。
```
[~/testGenerator]> python app.py
sat: ((a > 0)) & (((b < 2) & (c > 3)) & (((d == 2)) & ((e == 2))))
testcase: [c = 4, b = 1, a = 1, e = 2, d = 2]

sat: ((a > 0)) & (((b < 2) & (c > 3)) & ((d == 2)))
testcase: [c = 4, b = 1, a = 1, d = 2]

sat: ((a > 0)) & (((b < 2) & (c > 3)) & ((e == 2)))
testcase: [c = 4, b = 1, a = 1, e = 2]

sat: ((a > 0)) & (((b < 2) & (c > 3)) & ((f == 2)))
testcase: [a = 1, c = 4, b = 1, f = 2]

sat: ((a > 0)) & ((b < 2) & (c > 3))
testcase: [c = 4, b = 1, a = 1]

sat: (a > 0)
testcase: [a = 1]
```
