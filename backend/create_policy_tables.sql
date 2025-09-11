-- SQL script to create tables for finance and healthcare policy datasets

-- Table for finance policy data
CREATE TABLE finance_policy (
    id SERIAL PRIMARY KEY,
    country VARCHAR(100),
    year INT,
    adults_with_bank_account NUMERIC
);

-- Table for healthcare policy data
CREATE TABLE healthcare_policy (
    id SERIAL PRIMARY KEY,
    hospital_name VARCHAR(255),
    state CHAR(2),
    measure_name VARCHAR(100),
    score NUMERIC
);

-- Example COPY commands to import CSV data (update path as needed):
-- \copy finance_policy(country, year, adults_with_bank_account) FROM 'backend/datasets/finance_policy_sample.csv' DELIMITER ',' CSV HEADER;
-- \copy healthcare_policy(hospital_name, state, measure_name, score) FROM 'backend/datasets/healthcare_policy_sample.csv' DELIMITER ',' CSV HEADER;
