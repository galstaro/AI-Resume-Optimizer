import streamlit as st
import os
from dotenv import load_dotenv
import openai
from PyPDF2 import PdfReader
import json
import requests
from bs4 import BeautifulSoup
import tempfile
import base64

# Load environment variables
load_dotenv()

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set page config
st.set_page_config(
    page_title="AI Resume Optimizer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for the wavy background and theme
st.markdown("""
    <style>
    .stApp {
        background-color: #0a192f;
        color: #ffffff;
    }
    .main .block-container {
        background-color: #0a192f;
    }
    .stButton>button {
        background-color: #64ffda;
        color: #0a192f;
        border: none;
        padding: 15px 30px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #4cd8b2;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(100, 255, 218, 0.2);
    }
    .stTextInput>div>div>input {
        background-color: #112240;
        color: #ffffff;
        border: 1px solid #233554;
        border-radius: 8px;
        padding: 10px;
    }
    .stTextArea>div>div>textarea {
        background-color: #112240;
        color: #ffffff;
        border: 1px solid #233554;
        border-radius: 8px;
        padding: 10px;
    }
    .stFileUploader>div>div>div {
        background-color: #112240;
        border: 1px solid #233554;
        border-radius: 8px;
        padding: 10px;
    }
    .stMarkdown {
        color: #ffffff;
    }
    .stSubheader {
        color: #64ffda;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .stTitle {
        color: #64ffda;
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 30px;
    }
    .stInfo {
        background-color: #112240;
        border: 1px solid #233554;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    .stSpinner {
        color: #64ffda;
    }
    .stProgress .st-bo {
        background-color: #64ffda;
    }
    .stDownloadButton>button {
        background-color: #233554;
        color: #64ffda;
        border: 1px solid #64ffda;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stDownloadButton>button:hover {
        background-color: #64ffda;
        color: #0a192f;
    }
    .stMarkdown h3 {
        color: #64ffda;
        font-size: 24px;
        font-weight: bold;
        margin-top: 30px;
        margin-bottom: 20px;
    }
    .stMarkdown hr {
        border-color: #233554;
        margin: 20px 0;
    }
    /* New styles for better contrast */
    .stTextInput label, .stTextArea label, .stFileUploader label {
        color: #ffffff !important;
        font-weight: 500;
    }
    /* Target the file uploader text specifically */
    .stFileUploader > div:first-child {
        color: #ffffff !important;
    }
    .stFileUploader p {
        color: #ffffff !important;
    }
    .element-container div[data-testid="stFileUploader"] > div:first-child {
        color: #ffffff !important;
    }
    /* Override any inline styles */
    div[data-testid="stFileUploader"] div[data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
    }
    .stFileUploader > div > div > div > div {
        color: #ffffff !important;
    }
    .stTextArea > div > div > div > div {
        color: #ffffff !important;
    }
    .stInfo p {
        color: #ffffff !important;
    }
    .stSuccess {
        background-color: #112240;
        border: 1px solid #64ffda;
        color: #64ffda;
        padding: 10px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .stSuccess p {
        color: #64ffda !important;
        margin: 0;
    }
    .stMarkdown p {
        color: #ffffff !important;
    }
    .stMarkdown strong {
        color: #64ffda !important;
    }
    .stMarkdown li {
        color: #ffffff !important;
    }
    /* Modern Card Styling */
    .analysis-card {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .card-title {
        color: #64ffda;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .card-content {
        color: #ffffff;
        font-size: 1rem;
        line-height: 1.6;
    }
    .bullet-point {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        margin: 8px 0;
        padding-left: 10px;
    }
    .bullet-icon {
        min-width: 20px;
        color: #64ffda;
    }
    .section-divider {
        height: 1px;
        background: linear-gradient(to right, rgba(100, 255, 218, 0), rgba(100, 255, 218, 0.5), rgba(100, 255, 218, 0));
        margin: 30px 0;
    }
    </style>
""", unsafe_allow_html=True)

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file."""
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def analyze_resume(resume_text, job_description):
    """Analyze resume against job description using OpenAI API."""
    try:
        prompt = f"""Analyze the following resume against the job description and provide feedback in JSON format.
        You must respond with valid JSON only, using this exact structure:
        {{
            "missing_keywords": ["keyword1", "keyword2"],
            "skill_mismatches": ["mismatch1", "mismatch2"],
            "tone_improvements": ["improvement1", "improvement2"],
            "suggestions": ["suggestion1", "suggestion2"],
            "compatibility_score": 85
        }}
        
        Resume:
        {resume_text}
        
        Job Description:
        {job_description}
        
        Remember to:
        1. Use only the specified JSON structure
        2. Ensure all arrays have at least one item
        3. Make compatibility_score a number between 0-100
        4. Provide specific, actionable feedback in each category"""

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert resume analyzer. You must respond with valid JSON only, following the exact structure provided."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        # Get the response content
        content = response.choices[0].message.content.strip()
        
        # Validate JSON before returning
        try:
            # Parse the JSON to verify it's valid
            json.loads(content)
            return content
        except json.JSONDecodeError:
            # If JSON is invalid, return a properly formatted error JSON
            return json.dumps({
                "missing_keywords": ["Error: Could not analyze keywords"],
                "skill_mismatches": ["Error: Could not analyze skills"],
                "tone_improvements": ["Error: Could not analyze tone"],
                "suggestions": ["Error: Could not generate suggestions"],
                "compatibility_score": 0
            })

    except Exception as e:
        # Return a properly formatted error JSON
        return json.dumps({
            "missing_keywords": [f"Error: {str(e)}"],
            "skill_mismatches": ["Unable to complete analysis"],
            "tone_improvements": ["Unable to complete analysis"],
            "suggestions": ["Please try again or contact support if the issue persists"],
            "compatibility_score": 0
        })

def format_analysis_for_download(analysis_result):
    """Convert JSON analysis results into a readable text report."""
    try:
        results = json.loads(analysis_result)
        
        report = """AI RESUME OPTIMIZER - ANALYSIS REPORT
=================================

COMPATIBILITY SCORE
------------------
Overall Match: {}%

MISSING KEYWORDS
--------------
{}

SKILL MISMATCHES
---------------
{}

TONE IMPROVEMENTS
---------------
{}

SUGGESTIONS FOR IMPROVEMENT
------------------------
{}
""".format(
            results.get('compatibility_score', 0),
            "\n".join(f"• {keyword}" for keyword in results.get('missing_keywords', [])),
            "\n".join(f"• {mismatch}" for mismatch in results.get('skill_mismatches', [])),
            "\n".join(f"• {improvement}" for improvement in results.get('tone_improvements', [])),
            "\n".join(f"• {suggestion}" for suggestion in results.get('suggestions', []))
        )
        return report
    except Exception as e:
        return f"Error formatting analysis report: {str(e)}"

def main():
    # Title with custom styling
    st.markdown('<h1 class="stTitle">AI Resume Optimizer</h1>', unsafe_allow_html=True)
    
    # Introduction
    st.markdown("""
        <div style='background-color: #112240; padding: 20px; border-radius: 8px; border: 1px solid #233554; margin-bottom: 30px;'>
            <p style='color: #ffffff; font-size: 16px; line-height: 1.6;'>
                Upload your resume and paste a job description to get AI-powered feedback on how to optimize your resume for better chances of landing the job.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Create two columns for the main content
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<h2 class="stSubheader">Resume Upload</h2>', unsafe_allow_html=True)
        st.markdown("""
            <style>
            [data-testid="stFileUploader"] div:first-child {
                color: white !important;
            }
            </style>
        """, unsafe_allow_html=True)
        resume_file = st.file_uploader("Upload your resume (PDF)", type="pdf")
        resume_text = st.text_area("Or paste your resume text here", height=200)
        
        if resume_file:
            resume_text = extract_text_from_pdf(resume_file)
            st.markdown("""
                <div class="stSuccess">
                    <p>PDF successfully processed!</p>
                </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown('<h2 class="stSubheader">Job Description</h2>', unsafe_allow_html=True)
        job_link = st.text_input("Paste LinkedIn job link (optional)")
        job_description = st.text_area("Or paste job description here", height=200)
        
        if job_link:
            st.markdown("""
                <div class="stInfo">
                    <p>LinkedIn scraping functionality will be implemented in future updates.</p>
                </div>
            """, unsafe_allow_html=True)

    # Center the analyze button with custom styling
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button("Analyze Resume", use_container_width=True)

    if analyze_button and (resume_text or resume_file) and job_description:
        with st.spinner("Analyzing your resume..."):
            analysis_result = analyze_resume(resume_text, job_description)
            
            # Display results in a clean container with custom styling
            display_analysis_results(analysis_result)
            
            # Format the analysis for download
            formatted_analysis = format_analysis_for_download(analysis_result)
            
            # Add a download button for the formatted analysis
            st.download_button(
                label="Download Analysis Report",
                data=formatted_analysis,
                file_name="resume_analysis_report.txt",
                mime="text/plain"
            )

def display_analysis_results(analysis_result):
    """Display analysis results in a modern card layout."""
    try:
        # Try to parse the JSON result
        if isinstance(analysis_result, str):
            results = json.loads(analysis_result)
        else:
            results = analysis_result
        
        # Validate the required fields
        required_fields = ['missing_keywords', 'skill_mismatches', 'tone_improvements', 'suggestions', 'compatibility_score']
        for field in required_fields:
            if field not in results:
                results[field] = [] if field != 'compatibility_score' else 0
            if field != 'compatibility_score' and not isinstance(results[field], list):
                results[field] = [str(results[field])]
        
        # Missing Keywords Section
        st.markdown("""
            <div class="analysis-card">
                <div class="card-title">
                    🚫 Missing Keywords
                </div>
                <div class="card-content">
        """, unsafe_allow_html=True)
        
        for keyword in results.get('missing_keywords', []):
            st.markdown(f"""
                <div class="bullet-point">
                    <span class="bullet-icon">•</span>
                    <span>{keyword}</span>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Skill Mismatches Section
        st.markdown("""
            <div class="analysis-card">
                <div class="card-title">
                    ⚠️ Skill Mismatches
                </div>
                <div class="card-content">
        """, unsafe_allow_html=True)
        
        for mismatch in results.get('skill_mismatches', []):
            st.markdown(f"""
                <div class="bullet-point">
                    <span class="bullet-icon">•</span>
                    <span>{mismatch}</span>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Tone Improvements Section
        st.markdown("""
            <div class="analysis-card">
                <div class="card-title">
                    🎯 Tone Improvements
                </div>
                <div class="card-content">
        """, unsafe_allow_html=True)
        
        for improvement in results.get('tone_improvements', []):
            st.markdown(f"""
                <div class="bullet-point">
                    <span class="bullet-icon">•</span>
                    <span>{improvement}</span>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Suggestions Section
        st.markdown("""
            <div class="analysis-card">
                <div class="card-title">
                    ✨ Suggestions for Improvement
                </div>
                <div class="card-content">
        """, unsafe_allow_html=True)
        
        for suggestion in results.get('suggestions', []):
            st.markdown(f"""
                <div class="bullet-point">
                    <span class="bullet-icon">•</span>
                    <span>{suggestion}</span>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)

        # Add a section divider
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Compatibility Score
        score = results.get('compatibility_score', 0)
        st.markdown(f"""
            <div class="analysis-card">
                <div class="card-title">
                    🎯 Overall Compatibility Score
                </div>
                <div class="card-content" style="font-size: 2rem; text-align: center; color: #64ffda;">
                    {score}%
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    except json.JSONDecodeError:
        st.error("Error parsing analysis results.")
    except Exception as e:
        st.error(f"Error displaying results: {str(e)}")

if __name__ == "__main__":
    main() 