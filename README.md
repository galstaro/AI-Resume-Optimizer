# AI Resume Optimizer

A modern web application that uses AI to analyze and optimize your resume against job descriptions. Built with Streamlit and OpenAI's GPT-3.5.

## Features

- Upload PDF resumes or paste resume text
- Input job descriptions manually or via LinkedIn job links
- AI-powered analysis of resume-job description compatibility
- Detailed feedback on missing keywords, skill mismatches, and improvements
- Compatibility score visualization
- Modern, dark-themed UI with clean layout

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

1. Run the application:
   ```bash
   streamlit run app.py
   ```
2. Open your web browser and navigate to the URL shown in the terminal
3. Upload your resume or paste the text
4. Enter the job description
5. Click "Analyze Resume" to get AI-powered feedback

## Future Enhancements

- LinkedIn job description scraping
- Cover letter generation
- User authentication
- Resume section rewriting
- ATS optimization tips
- Resume templates

## Requirements

- Python 3.7+
- OpenAI API key
- Internet connection for API calls # AI-Resume-Optimizer
