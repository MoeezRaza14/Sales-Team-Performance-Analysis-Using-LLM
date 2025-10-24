import os
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
import pandas as pd
from mistralai import Mistral
from datetime import datetime

# Load environment variables
load_dotenv()
mistral_api_key = os.getenv("MISTRAL_API_KEY")
if not mistral_api_key:
    raise ValueError("Key not found")

# Initialize Mistral client
client = Mistral(api_key=mistral_api_key)

# Load sales data (assuming CSV is in the root; could add JSON support)
DATA_FILE = "F:/ms_vs_code_files/sales_performance_data.csv"  
try:
    df = pd.read_csv(DATA_FILE)
    # Clean data: Convert 'dated' to datetime, handle missing values
    df['dated'] = pd.to_datetime(df['dated'], errors='coerce')
    df = df.dropna(subset=['employee_id', 'dated'])  # Drop invalid rows
    df['employee_id'] = df['employee_id'].astype(int)
except FileNotFoundError:
    raise ValueError(f"Data file {DATA_FILE} not found")

app = FastAPI(title="Sales Performance Analysis API")

def get_llm_insights(prompt: str) -> str:
    """Helper to query LLM for insights."""
    try:
        response = client.chat.complete(
            model="mistral-large-latest",  # Strong model for better insights
            messages=[
                {"role": "system", "content": "You are a sales performance analyst. Provide qualitative feedback, strengths, weaknesses, and actionable insights."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

@app.get("/api/rep_performance")
def rep_performance(rep_id: int = Query(..., description="Unique ID of the sales rep")):
    """Get performance feedback for a specific rep."""
    rep_data = df[df['employee_id'] == rep_id]
    if rep_data.empty:
        raise HTTPException(status_code=404, detail="Rep not found")
    
    # Summarize key metrics
    summary = {
        "name": rep_data['employee_name'].iloc[0],
        "total_leads": int(rep_data['lead_taken'].sum()),
        "total_tours": int(rep_data['tours_booked'].sum()),
        "total_applications": int(rep_data['applications'].sum()),
        "total_revenue_confirmed": int(rep_data['revenue_confirmed'].sum()),
        "avg_tours_per_lead": rep_data['tours_per_lead'].mean(),
        "avg_apps_per_tour": rep_data['apps_per_tour'].mean(),
        "text_activity": rep_data[['mon_text', 'tue_text', 'wed_text', 'thur_text', 'fri_text', 'sat_text', 'sun_text']].sum().to_dict(),
        "call_activity": rep_data[['mon_call', 'tue_call', 'wed_call', 'thur_call', 'fri_call', 'sat_call', 'sun_call']].sum().to_dict(),
    }
    
    # Create prompt for LLM
    prompt = f"Analyze this sales rep's performance data: {summary}. Provide detailed feedback, strengths, areas for improvement, and 3 actionable suggestions."
    
    insights = get_llm_insights(prompt)
    return {"rep_id": rep_id, "insights": insights}

@app.get("/api/team_performance")
def team_performance():
    """Get overall team performance summary."""
    # Aggregate team metrics
    summary = {
        "total_reps": df['employee_id'].nunique(),
        "total_leads": int(df['lead_taken'].sum()),
        "total_tours": int(df['tours_booked'].sum()),
        "total_applications": int(df['applications'].sum()),
        "total_revenue_confirmed": int(df['revenue_confirmed'].sum()),
        "avg_tours_per_lead": df['tours_per_lead'].mean(),
        "avg_apps_per_tour": df['apps_per_tour'].mean(),
        "top_performers": df.groupby('employee_id')['revenue_confirmed'].sum().nlargest(3).to_dict(),
    }
    
    # Create prompt for LLM
    prompt = f"Analyze this overall sales team performance data: {summary}. Provide a summary, key strengths, challenges, and team-wide recommendations."
    
    insights = get_llm_insights(prompt)
    return {"insights": insights}

@app.get("/api/performance_trends")
def performance_trends(time_period: str = Query(..., description="Time period: monthly or quarterly")):
    """Get sales trends and forecasting."""
    if time_period not in ["monthly", "quarterly"]:
        raise HTTPException(status_code=400, detail="Invalid time_period. Use 'monthly' or 'quarterly'.")
    
    # Resample data by time period
    df.set_index('dated', inplace=True)
    if time_period == "monthly":
        aggregated = df.resample('M').agg({
            'lead_taken': 'sum',
            'tours_booked': 'sum',
            'applications': 'sum',
            'revenue_confirmed': 'sum'
        }).reset_index()
    else:  # quarterly
        aggregated = df.resample('Q').agg({
            'lead_taken': 'sum',
            'tours_booked': 'sum',
            'applications': 'sum',
            'revenue_confirmed': 'sum'
        }).reset_index()
    
    # Convert to dict for prompt
    trends_data = aggregated.to_dict(orient='records')
    
    # Create prompt for LLM (includes basic forecasting request)
    prompt = f"Analyze these sales trends over {time_period} periods: {trends_data}. Identify key trends, growth/decline patterns, and forecast future performance for the next period with reasons and 2 suggestions to improve."
    
    insights = get_llm_insights(prompt)
    return {"time_period": time_period, "insights": insights}