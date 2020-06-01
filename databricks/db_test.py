import sys
from pprint import pprint
import pyspark.dbutils
from pyspark.sql import SparkSession
spark = SparkSession.builder.getOrCreate()

dbutils = pyspark.dbutils.DBUtils(spark.sparkContext)
lmnt = dbutils.fs.ls("/mnt/jlazar")

with open("/home/john/code/emergent/rgn/model/tests.py", "rt") as f:
    buf = f.read()

dbutils.fs.put("/mnt/jlazar/123.txt", buf, overwrite=sys.maxsize)
pprint(lmnt)
