# Resume Builder Resources

This directory contains a collection of resources to help you build tailored resumes and cover letters for specific job applications. These documents consolidate information from your various historical resumes and other documents to create comprehensive reference materials.

## Files Included

### 1. `mega-resume.md`

This is your comprehensive "mega resume" that contains all your work experience, skills, and project details organized by role. Use this as your master reference when creating tailored resumes for specific job applications.

The document includes:
- About Me sections (Value Addition, Top Skills, Employee Description)
- Detailed Professional Experience by company/role
- Technical Skills breakdown
- Education & Certifications
- Personal Projects & Additional Skills
- Soft Skills & Work Style

### 2. `projects-by-category.md`

This file organizes your projects by skill category, making it easier to find relevant examples when tailoring your resume for specific job applications. Categories include:

- Data Analysis & Modeling (Predictive Modeling, Segmentation)
- Data Visualization & Dashboards
- Data Engineering & ETL
- Marketing & Campaign Analysis
- Financial Analysis
- Stakeholder Management & Requirements Gathering
- Personal Projects

### 3. `skills-and-criteria.md`

This document provides detailed responses to common selection criteria and highlights key skills that can be used when applying for jobs. It includes:

- Technical Skills (with evidence and example responses)
- Business and Soft Skills (with evidence and example responses)
- Selection Criteria Responses
- Common Interview Questions and Answers

## How to Use These Resources

### For Creating a Tailored Resume:

1. **Review the Job Description** - Identify key requirements, skills, and experiences that the employer is seeking.

2. **Select Relevant Experience** - From `mega-resume.md`, select the roles and projects that best demonstrate your alignment with the job requirements.

3. **Choose Relevant Projects** - From `projects-by-category.md`, select specific projects that highlight your relevant skills and accomplishments for the position.

4. **Address Selection Criteria** - If the job application requires addressing selection criteria, use `skills-and-criteria.md` to craft your responses.

5. **Tailor Your Resume** - Create a concise, targeted resume that emphasizes your most relevant experience, skills, and projects for the specific position.

### For Interview Preparation:

1. Review the common interview questions and answers in `skills-and-criteria.md`.

2. Prepare specific examples from your projects and experiences that demonstrate your capabilities.

3. Practice articulating your skills and experiences clearly and concisely.

## Best Practices

- **Be Selective** - Don't try to include everything from your mega resume in a tailored resume. Focus on the most relevant and impressive information.

- **Quantify Achievements** - Whenever possible, include measurable results and outcomes (e.g., "70-80% of new store sales fell within the forecasted range").

- **Customize for Each Application** - Take the time to customize your resume for each application rather than using a one-size-fits-all approach.

- **Keep it Concise** - Most resumes should be 2 pages maximum. Be selective about what you include.

- **Update Regularly** - Continue to update these master documents as you gain new experiences and skills.

## Maintaining These Documents

As you gain new experiences or complete new projects, remember to update these master documents to keep them current. This will ensure that you always have comprehensive, up-to-date information to draw from when creating tailored application materials.

# Resume Builder Templates

This directory contains HTML templates for generating professional resumes and cover letters, as well as a configuration file for populating these templates with your information.

## Template Files

- **resume-template.html**: A clean, professional resume template designed for modern job applications
- **cover-letter-template.html**: A matching cover letter template
- **template-config.env**: Configuration file containing all fields needed for both templates

## How to Use

1. **Edit the Configuration File**:
   - Open `template-config.env` in a text editor
   - Fill in your personal information, work experience, skills, and other details
   - For the cover letter, customize the paragraphs as needed for the specific job

2. **Generate Documents**:
   - The n8n workflow will automatically use these templates along with your configuration
   - The workflow will replace all placeholder fields with your actual information
   - The result will be custom-tailored resume and cover letter documents for your job application

3. **Customize Templates (Optional)**:
   - If needed, you can customize the HTML templates directly
   - The templates use standard HTML and CSS, making them easy to modify
   - The `--accent-color` variable in the resume template can be changed to match your personal brand

## Important Notes

- Keep your personal information secure in the configuration file
- The templates are designed to be print-friendly
- All styling is contained within the HTML files for portability

## Fields Explanation

The `template-config.env` file contains all the fields needed for both templates. Keys include:

- Personal information (name, contact details)
- Work experience details
- Skills categorized by type
- Education information
- Cover letter specific content

Each field in the configuration file corresponds to a placeholder in the templates that will be replaced during document generation. 