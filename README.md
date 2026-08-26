# Northwind Azure Data Engineering Pipeline

## Overview

An end-to-end data engineering project built using Azure Data Factory,
Azure Data Lake Storage Gen2, Azure Databricks, PySpark and Delta Lake.

The pipeline extracts data from a SQL Server Northwind database, dynamically
ingests multiple tables into Azure Data Lake Storage Gen2 as Parquet files,
and loads the raw data into Delta Bronze tables using Databricks.

The solution is designed to be reusable and parameter-driven rather than
creating a separate pipeline for every table.

---

## Architecture

```text
SQL Server
    |
    | Dynamic table extraction
    v
Azure Data Factory
    |
    | Lookup table metadata
    v
ForEach - Dynamic Table Processing
    |
    +------------------------------+
    |                              |
    v                              v
ADLS Gen2 Raw Layer          Databricks Serverless
    |                              |
    | Parquet                      | PySpark
    |                              |
    +--------------+---------------+
                   |
                   v
             Delta Bronze
          northwind.bronze
