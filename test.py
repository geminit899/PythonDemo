import pyarrow as pa
import pandas as pd
from pyspark import Row


if __name__ == '__main__':
    series = Row(id='id', name='name', age=22, test='xixi')
    df = pd.DataFrame(series.asDict(), index=[0])
    batch = pa.RecordBatch.from_pandas(df)
    print(1)
