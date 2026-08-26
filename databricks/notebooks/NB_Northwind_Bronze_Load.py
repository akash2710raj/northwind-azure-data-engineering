# Databricks notebook source
dbutils.widgets.text("tableName", "")
dbutils.widgets.text("folderName", "")

# COMMAND ----------

table_name = dbutils.widgets.get("tableName")
folder_name = dbutils.widgets.get("folderName")

print(f"Table: {table_name}")
print(f"Folder: {folder_name}")

# COMMAND ----------

source_path = f"abfss://northwind@northerwinds.dfs.core.windows.net/raw/{folder_name}/"
df = spark.read.parquet(source_path)
display(df)

# COMMAND ----------

target_table = f"northwind.bronze.{folder_name}"

df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable(target_table)

print(f"Created/updated: {target_table}")

# COMMAND ----------

