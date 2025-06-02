# Angus Gair - Mega Resume

## About Me

### Value Addition
1. **Analytics**  
   My background is in analytics—statistics and data science (predictive modelling). In addition to my IT and data skills, I bring a deep understanding of analytical thinking.
2. **Consulting**  
   I have worked with a wide range of clients in a consulting role (Equifax and MediaCom). One standout achievement was acting as the lead Analyst working on the Domino's France Project, where I was flown to France to deliver the results in person alongside the business consultant on the account.
3. **Industry Experience**  
   I have a diverse range of industry experience, including Banking (HSBC, AMEX), FMCG (Woolworths, Domino's Pizza), Media (Marketing & Advertising analysis), FinTech (Prospa and SocietyOne), and Political Voting (Labor Party).
4. **Large Datasets**  
   Domino's Pizza, Mastercard & HSBC at transactional level; Equifax Credit Bureau at individual level.

### Top Skills
1. **Marketing**  
   I studied a double major at university (Economics and Marketing) and have had exposure to marketing analytics in the majority of my roles (MediaCom, SocietyOne, Equifax). This experience gives me a strong grasp of revenue generation via customer acquisition, retention, segmentation, and ROI optimisation through cost per acquisition and lifetime value analysis.
2. **Ability to Work with Others and Stakeholder Management**
3. **Analytics and Modelling**
4. **Exposure to a Wide Range of Applications**  
   SQL Server and SSIS, Tableau, R, Python, Google Cloud and Azure Cloud platforms, SAS, Hadoop
5. **Adaptability and Mentorship**  
   I learn new skills quickly and also mentor more junior team members (I led a team of three at Equifax).

### Employee Description
- Diligent, self-motivated and works with great attention to detail  
- Not the loudest person in the room, but I build strong relationships over time  
- Enjoys the work I do  
- Thrives outside of my comfort zone—constantly learning new skills and exploring new areas  
- Keen on both data engineering and analytics/dashboarding/reporting  
- No formal education in data engineering yet, but would like to gain more experience and potentially move into this area in the future

## Professional Experience

### Sydney Trains
**Role:** Data Analyst

#### Project: PCM - Productivity Costing Model
- **Description:** By analyzing operational changes and decisions at each layer, the model offers an end-to-end view of cost accrual, providing insights not necessarily available in existing payroll functions or reports. It delivers a holistic and detailed look at when and where individual costs are incurred, enabling greater transparency around timetable decisions and associated servicing.
- **Scope:**
  - Staff: ~1,400 drivers and guards
  - Data Points: Wage payments, penalties, entitlements per Enterprise Agreement
- **Deliverables:** An end-to-end reporting tool capable of costing different layers of scheduling and rostering for Sydney Trains train crewing.
- **Data Model:**
  - Master (6–12-month View)
  - DWTT (6-week View)
  - Period (2-week)
  - Daily (1-day)
  - Actual (Costed by Payroll)
- **Considerations:** Wage, Absences, Allowances, Mileage, Penalties, Public Holidays, Minimum Shift Length
- **Impact:** In FY21 (June–December), about $15 million (~7% of total driver/guard labour costs) were related to excess shifts and extended hours.
- **Objectives:**
  1. Enable better financial management of train crew labour costs
  2. Create enhanced visibility, transparency and additional financial performance measures
- **Challenges:**
  - Over 130 pages of Enterprise Agreement conditions led to ~80 coded pay rules
  - Interaction between various entitlements (shift swaps, OTB—excess shift, WOBOD)
  - Multiple shifts, sometimes not tracked in front-end data
  - Discrepancies between front-end and back-end systems
  - Unofficial swaps and manual changes not captured systematically
- **Accomplishments:**
  1. Pay Breakdown: Expanded from one payroll metric (working hours) to seven categories of working time
  2. Pay Categorisation: Differentiated productive vs. unproductive costs
  3. Reporting Views: Aligned payroll cost model with both finance and enterprise agreement rules
  4. Documentation: Formalised previously ad hoc processes, mitigating key-person risk
- **Collaborations:** Payroll (SME), Train Crew Systems (BAU Owner), Master Schedule and Roster (SME), Workforce Modelling (SME), SPI Data & Analytics (data)
- **Data Quality & Reconciliation:**
  - Rounding assumptions must align with Payroll to two decimal places
  - Wage calculations reconciled against actual Payroll data from Finance
  - Payslip items reconciled for each specific line item
  - Across multiple data layers (SWTT, DWTT, Period, Actual), performed manual payslip checks
  - $70M in wages reconciled

#### Project: Passenger Weight Predictions
- **Description:** Predict passenger numbers based on Waratah train weights. This was particularly useful during fare-free travel initiatives introduced as part of Protected Industrial Action in 2022.
- **Implementation:** Travel was free on the Opal train network from 12.01am Monday 21 November 2022 to 11.59pm Friday 25 November 2022.
- **Accomplishments:** Built a Git repository documenting the process in detail (data ingestion, modelling steps, code versioning).
- **Skills Demonstrated:**
  - In my current role I have been responsible for Costing of the Train Networks Timetables. This is a complex piece of work that requires a deep understanding of Procedural Requirements (the process of creating rosters), Legal Requirements (Enterprise Bargaining Agreements) and System (technology) requirements. 
  - Built strong relationships with key stakeholders from Train Crewing (staff rostering), Payroll and ICT.
  - Solved various data issues including how to deal with multiple or conflicting pay entitlements, special cases not outlined in the Enterprise Agreement, and discrepancies in data between different source systems.
  - Extracted years of very specialized knowledge from stakeholders to document and code the end-to-end process for the first time.

### Equifax
**Role:** Senior Data Scientist / Lead Data Scientist

#### Project: Domino's New Store Model
- **Description:** Developed a dataset combining household demographics, commercial demographics, and business sales data. Created new variables (average distance of delivery, cost of goods, breakeven distance) and built two models forecasting pickup sales and delivery sales.
- **Objective:** Provide a report identifying the top 100 best new store locations.
- **Outcome:** Domino's Australia validated the forecasts by comparing actual new store sales against the modelled predictions. About 70–80% of new store sales fell within the forecasted range.
- **Challenges:**
  1. **Domino's France** – Equifax had no data assets in France, so I had to source household demographics, geographical information, commercial demographics, and business sales data.
  2. **Stability of Forecasts** – Models were rebuilt quarterly, requiring consistent stability of predictions.
- **Accomplishments:**
  - Built the "Delivery Distances Dashboard" for detailed operational performance views
  - Enabled territory visualisation and heat maps of deliveries
  - Provided store benchmarking capabilities
  - Recommended the next top 100 sites for new locations, which stores needed to reduce their store territory size and which stores were underperforming
  - Successfully rolled out the framework for Domino's New Zealand, Netherlands and France
- **Leadership:** As Lead Data Scientist, I facilitated fortnightly project update meetings and guided the team through complex analyses. I worked within a range of teams including marketing, head of franchise development, mapping analysts and project development, communicating via email, fortnightly calls and documentation of the methodology.

#### Project: ACTU (for the Australian Labor Party)
- **Description:** Created 13 models that identified voter intention (ALP, LNP, One Nation, etc.) and the top influential issues for each individual (climate change, economic management, immigration, etc.).
- **Usage:** For targeted campaigning via direct mail, telephone, and door-knocking.
- **Performance:** The Greens model had the largest uplift of 3.9x, verified by a live telephone poll conducted by ReachTel.
- **Data Sources:** 
  - Phone Polling responses (CSV formats)
  - Household geo-demographic data (SQL)
  - Past Year polling data (JSON)
- **Role and Responsibilities:**
  - As the Senior/Lead on the project, organized junior analysts in collating data from various sources into a single table for model building
  - Quality Control (QC) to ensure data accuracy
  - Documenting and cataloging code scripts via Git (for SQL and R languages)
  - Data matching in SQL
  - Providing guidance on data structure (e.g., prorating data to household level or rolling up individual data to household level)
- **Result:** Successfully delivered a single data model representing every household in Australia (approximately 10 million).

#### Additional Equifax Experience:
- Led a team during a transition into agile methodology
- This transition increased the number of projects completed within timelines, budget, and quality expectations
- Formulated the team vision and objectives in line with business strategy
- Connected team members to strategic requirements through regular communication and delegation
- Assisted with team members' career management including goal setting
- Built propensity models for AMEX (Platinum Cards) that were used to select prospects for direct mailing campaigns, achieving 1.8x uplift over previous campaigns
- Created a segmentation model for Credit Corp Personal Loans (Wallet Wizard), analyzing 1.4 million Bureau Credit enquiries over a 4-month period to identify top 10 competitors segmented by customer geo-demographic profiles

### Woolworths
**Role:** Senior Tableau Developer / Business Analyst

#### Project: Post Implementation Review (Automated Rostering)
- **Description:** Woolworths implemented a nationwide automated rostering system. Department managers typically spent ~8 hours a week doing rosters, and with 11 departments per store (88 hours per store weekly) and over 1,000 Woolworths stores nationwide, the objective was to reduce this administrative workload.
- **Duties:**
  1. Liaise with key stakeholders to understand business requirements
  2. Define business rules and logic for the data
  3. Collect data from various systems
  4. Build a data model with ongoing automated data refreshes
  5. Build and maintain dashboard reports
- **Dashboard Purpose:** Evaluate the effectiveness of the auto-scheduler in matching published rosters to forecast labour demand.
- **Granularity:**
  - **Store Manager:** Breakdown by department, day, hour (identifying where manual intervention was needed)
  - **Group Managers:** Responsible for multiple sites, needed a store-by-store breakdown
  - **Program Stakeholders:** Executive-level stakeholders needed overall progress updates on the rollout
- **Outcome:** The dashboard became the "source of truth" for program performance, informing decisions made by key stakeholders.
- **Challenges:**
  - Agreeing on KPI/OKR definitions
  - Determining the most effective data visualisations
  - Identifying essential metrics for the final dashboard
- **Data Sources:** Kronos Data, Employee Data, Sales Data, Forecast Sales

#### Additional Woolworths Experience:
- After completing the original project, worked as a Business Analyst to gather data requirements for building a Data Mart for the new automated rostering solution
- Worked in an Agile structure with End Users (e.g., Head of Finance), Data Developers, and Business Intelligence Analysts
- Translated end-user requirements into data requirements and schema designs for Data Developers
- Example: Converted a request to visualize store rosters as charts rather than tables into data requirements and created a visual representation of labor demand
- Worked on the rebuild of the store Planning and Performance Dashboard - the most used dashboard within Retail Analytics with hundreds of daily users
- Created dashboards with a strong focus on data integrity that helped continuously improve the auto-scheduler to reduce rostering costs

### Prospa
**Role:** Business Intelligence Analyst

- **Description:** Prospa is an Australian FinTech company that provides online lending services for small businesses.
- **Analysis Areas:**
  - USING SALESFORCE
  - Amortization of one-off fees
  - Monitoring default rates
- **Responsibilities:**
  - Writing SQL queries alongside data transformation and modeling
  - Building and maintaining internal and external contacts to facilitate data work in SAS
  - Working with complex data relationships and business rules

### SocietyOne
**Role:** Business Analyst (Sales and Marketing Team)

- **Description:** SocietyOne operates as a peer-to-peer lending platform connecting lenders with borrowers directly, bypassing traditional banks.
- **Analysis Areas:**
  - Campaign Reporting
  - Sales Funnel Analysis
  - Metrics & Dimensions
- **Marketing Channels:**
  - Display/Retargeting, Direct Mail, eDM, eDM (Paid), Paid Search, Partners/Affiliates, Organic/Website, Digital
- **Experience:**
  - Part of the team that built Data Marts for reporting
  - Moved raw data from production through an integrated ETL process to simplify data into a star schema ready for analysis
  - Tested data by querying tables to ensure accuracy between raw data layers, staging, business layers, and DataMart
  - Tested business logic and wrote queries for marketing reporting including direct mail campaigns, board level reporting, and customer service reports

### MediaCom / OMD
**Role:** Analytics Consultant

- Worked in analytics within a consulting capacity
- Applied statistical analysis techniques such as Regression, Population Analysis, Exploratory Analysis, ANOVA
- Used machine learning methods including Generalized Linear Models, Gradient Boosted Machines, and clustering techniques
- Addressed business questions such as:
  - Which media channels have the highest ROI?
  - Which individuals across Australia are most likely to become AMEX customers?
- Documented solutions and trained junior analysts
- Delivered results to external clients in high-quality presentations, reports, and dashboards

## Technical Skills

### Programming & Query Languages
- SQL (daily use for 7+ years with large datasets exceeding 100 million records)
- Python
- R
- SAS (Certified in "Predictive Modelling Using SAS InMemory Statistics" and "High-Performance Analytics")

### Data Visualization
- Tableau (Senior Developer)
- Power BI
- QlikView
- Excel (advanced functions)

### Platforms & Technologies
- SQL Server and SSIS
- Google Cloud Platform (GCP), including Hive SQL
- Azure Cloud
- Hadoop
- Git (for documentation and version control)

### Data Analysis Techniques
- Regression analysis
- Population analysis
- ANOVA
- Machine Learning (GLMs, Gradient Boosted Machines)
- Clustering
- Segmentation
- Propensity modeling

### Methodologies
- Agile
- JIRA
- Data warehousing concepts (star/snowflake schemas, data layering)

## Education & Certifications
- Double major at university: Economics and Marketing
- SAS Certifications:
  - "Predictive Modelling Using SAS InMemory Statistics Course"
  - "Predictive Modelling Using SAS High-Performance Analytics Procedures Course"

## Personal Projects & Additional Skills
- Personal interest in geo-spatial data
- Set up a home SQL server to integrate G-NAF data from data.gov.au with ABS demographics
- Created a visual dashboard of Australia at a Meshblock level (more granular than postcode)
- Experience with documentation and knowledge transfer

## Soft Skills & Work Style
- Diligent, self-motivated with great attention to detail
- Build strong relationships over time
- Thrive outside comfort zone and continuously learn new skills
- Strong communication skills (written and verbal)
- Stakeholder management and collaboration
- Time management and prioritization
- Adaptability in fast-changing environments
- Commitment to quality and accuracy
- Mentorship experience (led a team of three at Equifax) 