## testGenerator
Pythonコードをシンボリック実行により静的解析し、コード内のすべてのIfブロックに対するテスケースを生成するプログラムです。
シンボリック実行によってIfブロックへの到達制約をSMT問題に落としこみ、SMTソルバZ3によるテストケースの生成を行っています。
### 実行例
以下のように**if文を含んだ簡単なプログラム**を入力します。
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

### 実行例2
以下のように到達不可能なifブロックを入力します。
```
if __name__ == "__main__":
    sample = """
if a > 100 & a < 100:
    pass
"""
```
以下のように、unsatと出力されます。
```
[~/testGenerator]> python app.py
unsat: (a > 100) & (a < 100)
```


