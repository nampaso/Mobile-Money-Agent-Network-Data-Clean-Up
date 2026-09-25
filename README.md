# PLP Data Analytics Assignment 4: Agent Data Cleanup (`plp-da-a4-agent-data-cleanup`)

## Project Summary
This project implements an automated, programmatic data cleaning pipeline for agent transaction logs and agent registries. It addresses primary key deduplication, transaction type standardization, date ISO formatting, missing value imputation, outlier flagging via IQR, and referential integrity validation.

## Before-and-After Row Counts
* **Raw Transactions Row Count:** `1203`
* **Cleaned Transactions Row Count:** `1200`
* **Raw Agents Registry Row Count:** `52`
* **Cleaned Agents Registry Row Count:** `50`

## How to Regenerate Data and Run the Pipeline

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
