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

#### BWS Member-Match-Maker (MMM) Decision-Engine Health Check & Investment Review (Woolworths)
- Audited 14 months of campaign activity across 5.8M members, 1.1M redemptions and >£350M in sales
- Identified 3.27× faster basket growth for redemption baskets compared to control baskets
- Proved redeemers shop more frequently (every 1.45 weeks vs 1.67 weeks) driving +4.6 extra trips and +£216 per member per year
- Analysis led to recommendation to maintain fortnightly retargeting and expand high-propensity offer pools
- Secured approval for continued investment after confirming >£40M incremental sales

#### Marketing Mix Modeling Pipeline – Retail Loyalty Program (Woolworths)
- Engineered a robust, end-to-end data analytics pipeline for a major retail chain's loyalty program
- Integrated diverse data sources including transactions, customer profiles, campaign data, and TV market information
- Developed advanced SQL and data modeling logic for customer segmentation and campaign effectiveness measurement
- Created modular data framework with multi-stage ETL pipeline to support scalable analytics
- Implemented geographic segmentation with market structure analysis for urban and rural markets
- Designed sophisticated entity-relationship model connecting core business metrics
- Built processing capability for millions of monthly customer transactions
- Delivered actionable business intelligence for customer acquisition, retention, and program participation optimization

### Segmentation

#### Credit Corp Personal Loans Segmentation (Equifax)
- Analyzed 1.4 million Bureau Credit enquiries over a 4-month period
- Identified Credit Corp's top 10 competitors segmented by customer geo-demographic profiles
- Segmentation included age, gender, property value, education, disposable income, enquiry amount, credit score, etc.

#### Big W Rewards "Active Member" Redefinition (Woolworths)
- Analysed shopping-cycle behaviour for 10M+ Big W loyalty members using SQL in Google Cloud
- Discovered 82% of transactions occur within 8 weeks (vs 99% for Woolworths Supermarkets)
- Modelled the effect of tightening the "Active member" window from 26 weeks to 12 weeks
- Built a sensitivity-analysis framework and KPI dashboard quantifying changes in visit frequency, basket size and AOV
- Recommended a refreshed segmentation schema with new "Event Shoppers" layer for lifecycle marketing
- Received executive sign-off to adopt 12-week definition for FY-25 loyalty, promotional, and CRM budgets

## Data Visualization & Dashboards

#### Comprehensive Retail Loyalty Analytics Dashboard (Woolworths)
- Engineered an end-to-end data pipeline and analytics solution to monitor loyalty program performance
- Designed sophisticated data pipeline architecture integrating multiple data sources (transactions, customer profiles, campaigns, subscriptions)
- Implemented custom fiscal calendar mapping for retail-specific time analysis
- Produced a cohesive set of 18+ key performance metrics with comparative analysis
- Implemented advanced data processing techniques for customer segmentation and hierarchical member classification
- Built a scalable analytics framework with sophisticated entity-relationship model connecting core business metrics
- Delivered actionable business intelligence on customer acquisition, retention, subscription program growth, and member engagement
- Visualized performance trends with drill-down capabilities for program ROI and member value calculations

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

#### Retail Loyalty Program Analytics Dashboard – BIGW (Woolworths)
- Engineered comprehensive analytics platform for BIGW's retail loyalty program
- Built modular analytics framework capable of processing over 170 million transactions
- Delivered interactive dashboards and KPI visualizations for customer loyalty, campaign ROI, and subscription program growth
- Enabled automated month-over-month and year-over-year performance tracking
- Collaborated with marketing and business stakeholders to define metrics and ensure alignment with business goals

#### Points Cost Forecast System – BigW (Woolworths)
- Developed enterprise-scale forecast system for tracking and analyzing $52.3M in annual loyalty program costs
- Designed comprehensive ETL data pipeline in BigQuery SQL integrating finance, loyalty, campaign, and program data
- Architected multi-dimensional data model allowing analysis across business units, time periods, and campaign streams
- Developed sophisticated forecasting algorithms using basis point calculations achieving 97.8% forecast accuracy
- Created executive-level dashboards with drill-down analysis capabilities from high-level KPIs to detailed category performance
- Implemented multiple cost calculation methods (50bps, 70bps basis point models)
- Enabled business and category-level cost distribution with campaign-specific cost tracking
- Built forecasting capabilities for budget allocation optimization across business categories
- Developed variance analysis between forecast and actual costs with fiscal calendar alignment

#### Big W Stanhope Gardens Store Performance Diagnostic (Woolworths)
- Audited first 11 weeks of trading for new store using BigQuery SQL, Python, and Tableau
- Benchmarked against nearby stores to create like-for-like sales, foot-traffic, and loyalty baselines
- Identified Google rating issues (2.8 stars vs 4.1-4.2 for peer stores) correlating with lower basket size and repeat visits
- Diagnosed weak loyalty activation as chief commercial gap with member share six points lower than peers
- Built sensitivity framework linking Google-review lift, member sign-ups, and promotion uptake to revenue
- Recommendations led to store entering recovery track with improved member sign-ups and Google rating

## Data Engineering & ETL

#### Comprehensive Data Pipeline for BIGW Marketing (Woolworths)
- Developed a comprehensive data pipeline and analytics solution for the BIGW Marketing Team
- Designed and implemented a sophisticated ETL pipeline integrating multiple data sources:
  - Customer transaction data across 5 business destinations
  - Marketing campaign performance metrics (ATL/BTL)
  - Subscription program data (Everyday Extra)
  - Geographic market segmentation
  - Customer loyalty metrics
- Created a unified data model that maps customer behavior across different geographic markets
- Built a scalable analytics framework processing over 170M customer transactions
- Enabled granular analysis at store/postcode level with complex geographic segmentation
- Delivered actionable insights on key performance drivers by business unit, subscription program growth, and campaign effectiveness

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

#### AJ Insights Platform Development
- Developed a comprehensive platform combining CRM, website management, and analytics for small businesses
- Built an MVP Analytics Engine using Python, Pandas, and TensorFlow for advanced data analysis and predictive modeling
- Implemented five key pillars: Digital Presence, Customer Management, Data Management, Analytics, and AI Integration
- Created a seamless integration between customer relationship management system and client-facing web portal
- Implemented geo-spatial analytics and visualization tools for location-based business insights
- Developed AI-driven functionalities utilizing Anthropic AI, LangChain, and OpenAI API for automated content generation
- Designed a modern workflow orchestration enabling small businesses to leverage enterprise-grade data solutions

#### Geo-Spatial Data Integration
- Set up a home SQL server to integrate G-NAF data from data.gov.au with ABS demographics
- Created a visual dashboard of Australia at a Meshblock level (more granular than postcode)
- Applied data warehousing concepts learned from professional experience
