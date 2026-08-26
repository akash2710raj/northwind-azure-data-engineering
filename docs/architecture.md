# Architecture & Data Flow

## End-to-End Architecture

The Northwind data engineering solution follows a parameter-driven, multi-stage ingestion architecture:

```text
SQL Server
    |
    | Source tables
    v
Azure Data Factory
    |
    | Lookup
    | Retrieve table metadata
    v
ForEach
    |
    | tableName
    | folderName
    v
Copy Activity
    |
    | Parquet
    v
ADLS Gen2 - Raw Layer
    |
    | Databricks Serverless Job
    v
Databricks
    |
    | Reusable PySpark Notebook
    v
Delta Lake - Bronze Layer
```

---

## 1. Source Layer

The source system is a SQL Server Northwind database containing multiple relational tables.

Examples include:

- Customers
- Employees
- Orders
- Order Details
- Products
- Suppliers
- Categories

The pipeline is designed so that individual tables do not need separate hard-coded ingestion pipelines.

---

## 2. Azure Data Factory

Azure Data Factory acts as the orchestration layer.

### Lookup Activity

The Lookup activity retrieves the list of tables that need to be processed.

The resulting metadata is passed to a ForEach activity.

### ForEach Activity

The ForEach activity iterates over the table metadata.

For every iteration, the current table name is used to dynamically construct the required source and destination parameters.

Example:

```text
tableName  = Customers
folderName = customers
```

Another iteration might produce:

```text
tableName  = Order Details
folderName = order_details
```

This allows the same pipeline to process multiple tables.

---

## 3. ADLS Gen2 Raw Layer

The Copy Data activity moves the source data from SQL Server to Azure Data Lake Storage Gen2.

The raw data is stored as Parquet.

Example folder structure:

```text
raw/
├── customers/
├── employees/
├── orders/
├── order_details/
├── products/
└── ...
```

The folder name is generated dynamically from the current table.

---

## 4. Databricks Serverless Processing

After the Copy activity succeeds, Azure Data Factory triggers the Databricks Serverless Job.

The Job executes the reusable:

```text
NB_Northwind_Bronze_Load
```

PySpark notebook.

The ADF Job activity dynamically passes:

```text
tableName
folderName
```

to the Databricks Job.

Example:

```text
tableName  = Customers
folderName = customers
```

The same notebook can therefore process any table in the pipeline.

---

## 5. PySpark Notebook

The notebook retrieves the parameters using Databricks widgets.

Conceptually:

```python
table_name = dbutils.widgets.get("tableName")
folder_name = dbutils.widgets.get("folderName")
```

The folder parameter is then used to construct the source path:

```text
/raw/<folder_name>/
```

The corresponding Parquet data is read using Spark and written into the Delta Bronze layer.

---

## 6. Delta Bronze Layer

The processed data is stored as Delta tables under the Northwind Bronze schema.

Examples:

```text
northwind.bronze.customers
northwind.bronze.employees
northwind.bronze.orders
northwind.bronze.order_details
northwind.bronze.products
```

The same notebook and orchestration pattern is reused for all tables.

---

## 7. Serverless Compute

The Databricks Bronze processing is implemented using a Databricks Serverless Job.

This removes the need to maintain a persistent interactive cluster for the pipeline and allows compute to be managed by the Databricks platform.

---

## 8. Parameter Flow

The key design principle is parameter propagation across the pipeline:

```text
ADF Lookup
    |
    v
ForEach current item
    |
    +-- tableName
    |
    +-- folderName
    |
    v
Databricks Job
    |
    v
PySpark Notebook
    |
    +-- tableName
    |
    +-- folderName
    |
    v
Dynamic ADLS path
    |
    v
Delta Bronze table
```

This makes the solution reusable and minimizes hard-coded table-specific logic.

---

## 9. Source Control

Azure Data Factory is connected to GitHub for source control.

ADF-generated resources are maintained as JSON definitions, while the Databricks notebook is maintained as a Python source file.

The repository also contains sanitized example linked-service configurations for documentation.

---

## 10. Security Considerations

Credentials and secrets are not documented in the portfolio artifacts.

Production implementations should use secure authentication mechanisms such as:

- Azure Key Vault
- Managed Identity
- Secure linked-service configuration

Access tokens, passwords, storage keys, SAS tokens and other secrets should never be committed to source control.

---

## Design Summary

The architecture demonstrates a reusable cloud data engineering pattern:

**SQL Server → Azure Data Factory → ADLS Gen2 → Databricks Serverless → Delta Lake**

The use of metadata-driven processing, dynamic parameters and a reusable PySpark notebook allows the solution to scale across multiple source tables without duplicating pipeline logic.
