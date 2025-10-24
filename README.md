# Sales Team Performance Analysis Backend

This project is a backend system that uses a Large Language Model (LLM) to analyze sales data and provide feedback on both individual sales representatives and the overall sales team. It implements RESTful APIs to deliver performance insights, leveraging Mistral AI for qualitative analysis.

## Architecture Overview
- **Framework**: FastAPI is used to create lightweight, asynchronous RESTful APIs.
- **Data Handling**: Pandas processes and aggregates sales data from a CSV file.
- **LLM Integration**: Mistral AI API generates qualitative insights and actionable suggestions from summarized metrics.
- **Environment**: Python 3.14.0+. Runs locally with no database or cloud deployment required.
- **Data Flow**: Load CSV → Filter/Aggregate data per endpoint → Summarize as text → Prompt Mistral LLM → Return JSON response.

Technologies: FastAPI, Pandas, Mistral AI, python-dotenv.

## Setup Instructions
1. **Clone the Repository**
2. **Install Dependencies**
- Download the requirements.text file
- Enter a valid API key for LLM that you are using (In our case its Mistral).
4. **Prepare Data**:
- Ensure `sales_performance_data.csv` is in the project directory .
5. **Run the Server**:
- Start the application: `uvicorn main:app --reload`.
- The API will be available at `http://127.0.0.1:8000`.

## How to Run and Test
- **Start the Server**: Use the command above and keep the terminal open.
- **Test with Postman**:
- Create GET requests on Postman for the following endpoints:
1. **Individual Rep Performance**: `http://127.0.0.1:8000/api/rep_performance?rep_id=183`
  - Params: Key=`rep_id`, Value=`183` (or another valid `employee_id`).
  - Expected: JSON with rep-specific insights.
2. **Team Performance**: `http://127.0.0.1:8000/api/team_performance`
  - No params.
  - Expected: JSON with team-wide insights.
3. **Performance Trends**: `http://127.0.0.1:8000/api/performance_trends?time_period=monthly`
  - Params: Key=`time_period`, Value=`monthly` (or `quarterly`).
  - Expected: JSON with trend analysis and forecasts.
- Save requests in a collection (e.g., "Sales API Tests") for documentation.
- **Example curl Commands**:
- curl `http://127.0.0.1:8000/api/rep_performance?rep_id=183`
- curl `http://127.0.0.1:8000/api/team_performance`
- curl `http://127.0.0.1:8000/api/performance_trends?time_period=monthly`
