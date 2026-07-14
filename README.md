# Cloud Migration Validation Framework

## Objective

This project demonstrates automated validation of cloud data migrations between AWS and GCP.

It validates:

- Schema parity
- Row count parity
- Duplicate detection
- Null validation
- Hash comparison
- File validation
- Image validation
- Video validation
- Metadata validation
- Bronze/Silver/Gold validation

We built a cloud migration validation framework that simulates AWS-to-GCP data migration. It validates schemas, row counts, nulls, duplicates, checksums, image and video integrity, and generates evidence reports. I built it in Python, SQL, and PySpark using a modular architecture because I wanted to deepen my understanding of the exact challenges involved in migration validation.

### DATA VALIDATION PILLARS

We have 8 validation pillars**, which are also common in industry.

# 1. Data Profiling (Understand the data), we called it data overview in DS

This happens **before** validation.

Checks include:

* Number of rows
* Number of columns
* Column names
* Data types
* Memory usage
* Missing values
* Percentage of missing values
* Duplicate rows
* Duplicate primary keys
* Unique values per column
* Numeric summary (min, max, mean, std)
* Categorical summary
* Sample records
* Statistics Summary  and many more

**Output:** "What does my dataset look like?"

---

# 2. Schema Validation

Checks:

* Column names match
* Column order (if required)
* Data types match
* Required columns exist
* Unexpected columns
* Nullable vs non-nullable columns
* Schema drift

Example:

Source

```
CustomerID INT
```

Target

```
CustomerID STRING
```

❌ Fail

---

# 3. Completeness Validation

Checks:

* Null values
* Empty strings
* Missing files
* Missing records
* Missing partitions
* Missing images
* Missing videos
* Missing metadata

Example:

```
Customer Name = NULL
```

---

# 4. Uniqueness Validation

Checks:

* Duplicate rows
* Duplicate primary keys
* Duplicate business keys
* Duplicate filenames
* Duplicate image IDs

Example:

```
ProductID

1101

1101
```

❌ Duplicate

---

# 5. Validity Validation

Checks:

* Correct data types
* Valid dates
* Valid email format
* Valid phone numbers
* Valid country codes
* Numeric columns contain only numbers
* Allowed categorical values

Example

```
Quantity

two hundred
```

instead of

```
200
```

❌ Invalid

---

# 6. Consistency / Parity Validation

This is huge for migrations.

Checks:

* Row count parity
* Column parity
* Value parity
* Aggregate parity
* Checksums
* Hash comparison
* Source vs target comparison
* Metadata comparison

Example

Source

```
Price = 10
```

Target

```
Price = 15
```

❌ Fail

---

# 7. Integrity Validation

Checks:

* Primary key integrity
* Foreign key integrity
* Referential integrity
* Parent-child relationships
* Orphan records

Example

Orders

```
CustomerID = 5
```

Customer table

```
CustomerID = 5
```

doesn't exist.

❌ Fail

---

# 8. Business Rule Validation

These depend on the business.

Warehouse example:

* Quantity ≥ 0
* Price > 0
* Status must be:

```
In Stock

Out of Stock

Reserved
```

Category must be

```
Electronics

Furniture

Toys
```

Restocked date

Cannot be in the future.

---

# For Images

Checks

* Missing images
* Corrupt images
* Resolution
* Width
* Height
* Image format
* Duplicate images
* Missing labels
* Metadata consistency

---

# For Videos

Checks

* Missing videos
* Corrupt videos
* FPS
* Frame count
* Duration
* Resolution
* Codec
* Missing annotations

---

# For Text

Checks

* Empty text
* Duplicate text
* Invalid language
* Missing labels
* Token count
* Encoding
* Offensive content labels
* Metadata consistency

---

# For Migration Validation (AWS → GCP)

Checks

* Schema parity
* Row count parity
* Hash comparison
* Object count
* File size parity
* Checksum parity
* Metadata parity
* Partition parity
* Replication lag
* DAG completion
* Data quality alerts
* Pipeline logs
* Retry validation

# The order we would build this project

```text
validation/

│

├── data_profiler.py

├── schema_validator.py

├── completeness_validator.py

├── uniqueness_validator.py

├── validity_validator.py

├── consistency_validator.py

├── integrity_validator.py

├── business_rule_validator.py

├── migration_validator.py

└── report_generator.py
```

## Why this structure?

We like this architecture because it's **principle-based**, not dataset-based. Whether you're validating warehouse data, customer records, images, videos, or text, you're asking the same kinds of questions:

* Is the schema correct?
* Is the data complete?
* Is it unique?
* Is it valid?
* Is it consistent with the source?
* Does it maintain integrity?
* Does it satisfy the business rules?

That makes your framework reusable across different projects—the kind of design decision interviewers often appreciate because it shows you're thinking beyond a single dataset.


#### Migrating AWS s3 to GCS, what validation do we do
For S3 to GCS migration, I would validate first at object level by comparing object counts, paths, sizes, metadata, and checksums. Then I would validate at content level by reading the migrated datasets and checking schema, row counts, missing records, duplicates, nulls, business rules, and source-target parity. That gives both transfer integrity and data quality evidence for migration sign-off. The goal of the validation framework is to compare data before and after cloud migration. At the object level, it checks that files moved from S3 to GCS completely. At the content level, it validates schema, row counts, duplicates, missing records, nulls, checksums, and business rules. The final output is an evidence report showing whether the migrated data is ready for acceptance sign-off.


## Data completness checks
we are checking to know if the data is complete or not. columns_with_completeness_issues:
- Quantity
- Price
- Last Restocked

And for each column, we get information on the :

null_nan_count
empty_string_count
whitespace_only_count
total_missing_count
missing_percentage
sample_missing_rows

So it answers both questions:

Which columns have completeness issues?
What exactly is wrong in each column?

### What uniqueness validation checks

For your warehouse dataset:

Product ID

should be unique.

So we check:

duplicate full rows
duplicate primary keys
duplicate business keys, if needed
sample duplicate records
duplicate count per key

### primary key vs Business key
A primary key is a database constraint used to uniquely identify a record, while a business key is based on business rules and may consist of one or more columns that should uniquely identify a real-world entity. During migration validation, I check primary keys to ensure database integrity, and I can also validate business keys to detect logical duplicates that violate business requirements.


# validation_rules.yaml file
│
├── required_columns        → Completeness Validator
├── expected_data_types     → Schema Validator
├── numeric_columns         → Validity Validator
├── date_columns            → Validity Validator
├── allowed_values          → Validity Validator
├── business_rules          → Business Rule Validator
└── compare_columns         → Source-Target Parity Validator

"Each validator reads only the configuration relevant to its responsibility. The validation engine is generic, while dataset-specific rules are externalized in YAML."

#### Questions

1., Design and implement automated data validation pipelines comparing AWS and GCP outputs using Python and Databricks"

What we're building:

Source Dataset
        ↓
Load Dataset
        ↓
Data Profiling
        ↓
Schema Validation
        ↓
Completeness Validation
        ↓
Uniqueness Validation
        ↓
Validity Validation
        ↓
Parity Validation
        ↓
Business Rule Validation
        ↓
Migration Report
We do this in Python Pandas and then we  replace pandas with Pyspark/databric later.