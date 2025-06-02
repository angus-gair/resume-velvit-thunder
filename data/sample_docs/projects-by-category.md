# Projects By Category

This document organizes projects by skill category to make it easier to find relevant examples when tailoring your resume for specific job applications.

## Data Analysis & Modeling

### Predictive Modeling

#### Domino's New Store Model (Equifax)
- Built two models forecasting pickup sales and delivery sales for new store locations
- Developed a dataset combining household demographics, commercial demographics, and business sales data
- Created new variables (average distance of delivery, cost of goods, breakeven distance)
- Provided a report identifying the top 100 best new store locations
- 70–80% of new store sales fell within the forecasted range
- Rolled out the framework for Domino's New Zealand, Netherlands, and France

#### ACTU Voter Models (Equifax)
- Created 13 models that identified voter intention (ALP, LNP, One Nation, etc.)
- Models also identified top influential issues for each individual (climate change, economic management, immigration, etc.)
- Used for targeted campaigning via direct mail, telephone, and door-knocking
- The Greens model had the largest uplift of 3.9x, verified by live telephone poll
- Delivered a single data model representing every household in Australia (approximately 10 million)

#### Passenger Weight Predictions (Sydney Trains)
- Predicted passenger numbers based on Waratah train weights
- Particularly useful during fare-free travel initiatives in 2022
- Built a Git repository documenting the process in detail (data ingestion, modeling steps, code versioning)

#### AMEX Platinum Cards Model (Equifax)
- Built propensity models used to select prospects for direct mailing campaigns
- Achieved 1.8x uplift over previous campaigns

### Segmentation

#### Credit Corp Personal Loans Segmentation (Equifax)
- Analyzed 1.4 million Bureau Credit enquiries over a 4-month period
- Identified Credit Corp's top 10 competitors segmented by customer geo-demographic profiles
- Segmentation included age, gender, property value, education, disposable income, enquiry amount, credit score, etc.

## Data Visualization & Dashboards

#### Delivery Distances Dashboard (Equifax)
- Provided detailed view of store's operational performance
- Enabled territory visualization and heat map of deliveries
- Integrated cost, revenue, and profit metrics
- Added benchmarking capabilities to compare stores

#### Implementation Review Dashboard (Woolworths)
- Evaluated effectiveness of auto-scheduler in matching published rosters to forecast labor demand
- Created visualizations for three different user groups:
  - Store Managers: department, day, hour breakdowns
  - Group Managers: store-by-store comparisons
  - Program Stakeholders: overall rollout progress
- Became the "source of truth" for program performance
- Informed key decisions that improved the auto-scheduler

#### Planning and Performance Dashboard (Woolworths)
- Most used dashboard within Retail Analytics with hundreds of daily users
- Focused on data integrity and auto-scheduler performance
- Helped continuously improve the auto-scheduler to reduce rostering costs

## Data Engineering & ETL

#### PCM - Productivity Costing Model (Sydney Trains)
- Built an end-to-end reporting tool for costing different layers of scheduling and rostering
- Created a multi-layer data model with different time horizons:
  - Master (6–12-month View)
  - DWTT (6-week View)
  - Period (2-week)
  - Daily (1-day)
  - Actual (Costed by Payroll)
- Reconciled $70M in wages against actual Payroll data
- Implemented complex business rules (80+ pay rules from 130+ pages of Enterprise Agreement)
- Handled data quality issues and discrepancies between systems

#### Data Mart for Automated Rostering (Woolworths)
- Gathered data requirements to build a Data Mart for a new automated rostering solution
- Translated end-user requirements into data requirements and schema designs
- Worked with data from multiple systems: Kronos, WorkIam, SAP, GCP
- Merged data at different granularity levels (daily, hourly, transactional, dimensional)

#### SocietyOne Data Marts
- Moved raw data from production through an integrated ETL process
- Simplified complex snowflake schema into a star schema ready for analysis
- Tested data by querying tables to ensure accuracy between raw data layers, staging, business layers, and DataMart
- Wrote queries for marketing reporting including direct mail campaigns, board level reporting, and customer service reports

## Marketing & Campaign Analysis

#### SocietyOne Campaign Reporting
- Analyzed sales funnel and campaign performance
- Worked with multiple marketing channels: Display/Retargeting, Direct Mail, eDM, Paid Search, Partners/Affiliates, Organic/Website
- Created reports for direct mail campaigns and board level reporting

#### MediaCom/OMD Media Channel ROI Analysis
- Applied statistical analysis techniques to determine which media channels have the highest ROI
- Used regression, population analysis, and exploratory analysis methods
- Delivered results to external clients in high-quality presentations, reports, and dashboards

## Financial Analysis

#### Prospa Financial Analysis
- Analyzed amortization of one-off fees
- Monitored default rates for small business loans
- Worked with Salesforce data and complex financial relationships

## Stakeholder Management & Requirements Gathering

#### Automated Rostering Implementation (Woolworths)
- Liaised with key stakeholders to understand business requirements
- Defined business rules and logic for data
- Collected data from various systems
- Built a data model with ongoing automated data refreshes
- Collaborated with End Users (e.g., Head of Finance), Data Developers, and Business Intelligence Analysts

#### Train Networks Timetables (Sydney Trains)
- Built strong relationships with key stakeholders from Train Crewing, Payroll, and ICT
- Extracted specialized knowledge to document complex processes
- Navigated procedural requirements, legal requirements (Enterprise Agreements), and system requirements
- Solved complex data issues including conflicting pay entitlements and discrepancies between systems

## Personal Projects

#### Geo-Spatial Data Integration
- Set up a home SQL server to integrate G-NAF data from data.gov.au with ABS demographics
- Created a visual dashboard of Australia at a Meshblock level (more granular than postcode)
- Applied data warehousing concepts learned from professional experience 