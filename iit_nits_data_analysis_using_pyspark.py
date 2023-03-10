# -*- coding: utf-8 -*-
"""IIT-NITs DATA ANALYSIS USING PYSPARK.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1QS_iR6KKPFEOaRQYmDqjz65xeIx4XIjR

**SETTING UP A PYSPARK ENVIRONMENT**
"""

# Download Java Virtual Machine (JVM)
!apt-get install openjdk-8-jdk-headless -qq > /dev/null

# Download Spark
#!wget -q https://dlcdn.apache.org/spark/spark-3.2.1/spark-3.2.1-bin-hadoop3.2.tgz
!wget -q https://archive.apache.org/dist/spark/spark-3.0.1/spark-3.0.1-bin-hadoop3.2.tgz
# Unzip the file
!tar xf spark-3.0.1-bin-hadoop3.2.tgz

import os
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"
os.environ["SPARK_HOME"] = '/content/spark-3.0.1-bin-hadoop3.2'

# Install library for finding Spark
!pip install -q findspark
# Import the libary
import findspark
# Initiate findspark
findspark.init()
# Check the location for Spark
findspark.find()

"""**UPLOADING DATA FILE FOR THE IIT/NIT OPENING AND CLOSING RANK ANALYSIS**"""

from google.colab import files

files.upload()

"""**INITIATING PYSPARK SESSION**"""

# Import SparkSession
from pyspark.sql import SparkSession
# Create a Spark Session
spark = SparkSession.builder.master("local[*]").getOrCreate()
# Check Spark Session Information
spark

"""**READING DATA**"""

df = spark.read.format("csv").option("header","true").option("inferSchema","true").option("mode","failfast").load("data.csv")

df.count()

df.createOrReplaceTempView("iit")

"""**DATA DICT/DESCRIPTION**"""

spark.sql("select * from iit").show()
#About Data
"""In this dataset, the year-wise distribution of cutoffs for various IITs and NITs are collected and organized on the basis of stream, category, quota etc."""
# Data Dictionary
"""Variable	        Definition	                                                          Key
year	            The year of the conducted JEE exam	
institute_type	  Type of Institute (IIT or NIT)	
round_no	        The counseling round number	
quota	            The reservation quota	                                                AI: All-India, HS: Home-State, OS: Other-State, AP: Andhra Pradesh, GO: Goa, JK: Jammu & Kashmir, LA: Ladakh
pool	            The gender quota	
institute_short	  THe short name of the Institution	
program_name	    The name of the program/stream	
program_duration	The duration of the course (in years)	
degree_short	    The name of the degree (Abbreviated)	
category	        The caste category	                                                  GEN: General, OBC-NCL: Other Backward Classes-Non Creamy Layer, SC: Scheduled Castes, ST: Scheduled Tribes, GEN-PWD: General & Persons with Disabilities, OBC-NCL-PWD: Other Backward Classes & Persons with Disabilities, SC-PWD: Scheduled Castes & Persons with Disabilities, ST-PWD: Scheduled Tribes & Persons with Disabilities, GEN-EWS: General & Economically Weaker Section, GEN-EWS-PWD: General & Economically Weaker Section & Persons with Disability
opening_rank	    The opening (starting) rank for getting admission in the institution	
closing_rank	    The closing (ending) rank for getting admission in the institution	
is_preparatory	  If admission to a preparatory course is available	                    0: No, 1: Yes"""

"""**DATA ANALYSIS USING PYSPARK SQL FUNCTION**

**1. average opening ranks as per the institution type**
"""

spark.sql("select avg(opening_rank),institute_type from iit group by institute_type").show()

"""**2. Avg round numbers that are gone as per the program name sort them by avg round no.**"""

spark.sql("select avg(round_no) as avg_round,program_name from iit group by program_name order by avg_round").show()

"""**3. The count of unique categories as per the program name for the institute of IIT-Bombay.**"""

spark.sql("select count(distinct category),program_name from iit where institute_short ='IIT-Bombay' group by program_name ").show()

"""**4. the average opening and closing rank for the institute IIT-Bombay for year 2016**"""

spark.sql("select avg(opening_rank),avg(closing_rank) from iit where institute_short ='IIT-Bombay' and year = 2016").show()

"""**5. listing year,institute_type,average opening_rank and closing_rank as per year and institute and sort them by year.**"""

spark.sql("select year,institute_type,avg(opening_rank),avg(closing_rank) from iit group by 1,2 order by year").show()

"""**6. giving the average closing rank as per the program name sort them by program name.**"""

df.groupBy("program_name").avg("closing_rank").orderBy("program_name").show()

"""**7. listing the unique category for the is_preparatory was enabled.**"""

spark.sql("select distinct category from iit where is_preparatory = 1").show()

"""**8. listing the unique program name where is_preparatory was enabled.**"""

spark.sql("select distinct program_name from iit where is_preparatory = 1 ").show()

"""**using window function answering certain questions**"""

import pyspark.sql.functions as F
from pyspark.sql import Window
import pyspark.sql.types as T

"""**partitioning the data as per the institute**"""

windowSpec = Window.partitionBy("institute_type")

"""**analysing the data by adding two more fields of average opening and closing rank as per the institute type**"""

data = df.withColumn("avg_opening_rank",F.avg(F.col("opening_rank")).over(windowSpec)).withColumn("avg_closing_rank",F.avg(F.col("closing_rank")).over(windowSpec))

data.show()

"""**showing the cummulative result for the avg openign and closing rank as per the institute type**"""

data1 = df.groupBy("institute_type").agg(
    F.expr("avg(opening_rank)").alias("avg_opening_rank"),
    F.expr("avg(closing_rank)").alias("avg_closing_rank")
)

data1.show()