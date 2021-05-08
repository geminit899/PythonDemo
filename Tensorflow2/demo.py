from pyspark import Row
import pandas as pd

if __name__ == '__main__':
    data = []
    data.append(Row(name='tyx', age=18, gender=1))
    data.append(Row(name='xxr', age=22, gender=1))
    data.append(Row(name='zm', age=18, gender=0))
    df = pd.DataFrame(data, columns=['age', 'gender', 'name'])
    tt = df[df['age'].isin([18])]
    print(1)
