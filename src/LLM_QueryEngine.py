import os
import sys
from pathlib import Path

from openai import OpenAI, APIError
from dotenv import load_dotenv
from sqlalchemy import text

# Add the project root to Python path so imports work regardless of where the app is launched.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from data.db_connect import engine, get_database_schema

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client
#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY_QWEN"))
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)


def is_safe_query(sql_query: str) -> bool:
    """
    Checks if the generated SQL contains dangerous keywords.
    Returns True if safe, False if dangerous.
    """
    dangerous_keywords = [
        "DROP", "DELETE", "UPDATE", "INSERT", 
        "ALTER", "TRUNCATE", "EXEC", "GRANT", "REVOKE"
    ]
    sql_upper = sql_query.upper()
    for keyword in dangerous_keywords:
        if keyword in sql_upper:
            print(f"🚨 SECURITY BLOCK: Detected dangerous keyword '{keyword}' in query!")
            return False
    return True

def ask_database(question: str) -> str:
    """
    Main function: Takes a natural language question,
    converts it to SQL, runs it, and returns a human answer.
    """
    # We wrap the ENTIRE function in one giant try-except block.
    # This guarantees NO ERROR ever bubbles up to app.py.
    try:
        schema = get_database_schema()

        system_prompt = f"""You are an expert SQL assistant. You have access to a SQLite database 
with the following schema:

{schema}

Your job:
1. Convert the user's natural language question into a valid SQLite SQL query.
2. ONLY return the SQL query. No explanations, no markdown, no backticks.
3. Use proper JOINs when data spans multiple tables.
4. If the question cannot be answered with the available data, return: "I cannot answer this with the available data."

Important rules:
- Use SQLite syntax.
- Never use DELETE, DROP, UPDATE, or INSERT. Only SELECT queries are allowed.
"""

        # PHASE 1: GENERATE SQL
        response = client.chat.completions.create(
            model="qwen/qwen3-32b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0
        )

        sql_query = response.choices[0].message.content.strip()

        # Clean up any markdown formatting the LLM might add
        if sql_query.startswith("```"):
            sql_query = sql_query.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        print(f"\n🔍 Generated SQL:\n{sql_query}\n")

        # PHASE 2: SAFETY CHECK & EXECUTE
        if not is_safe_query(sql_query):
            return "🚫 **Security Alert:** I cannot execute this query because it contains potentially destructive commands. I am only allowed to read data (SELECT)."

        with engine.connect() as connection:
            result = connection.execute(text(sql_query))
            rows = result.fetchall()
            columns = result.keys()

        if not rows:
            return "The query returned no results."

        result_text = ""
        for row in rows:
            result_text += " | ".join([f"{col}: {val}" for col, val in zip(columns, row)]) + "\n"

        print(f"📋 Raw Results:\n{result_text}")

        # PHASE 3: CONVERT RAW DATA TO HUMAN ANSWER
        explanation_prompt = f"""The user asked: "{question}"

The SQL query returned these results:
{result_text}

Please provide a clear, concise, and friendly answer in plain English. 
Include specific numbers and details from the data. Do NOT mention SQL or technical terms."""

        explanation_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful data analyst who explains database results in simple, business-friendly language."},
                {"role": "user", "content": explanation_prompt}
            ],
            temperature=0.3
        )

        return explanation_response.choices[0].message.content.strip()

    # ==========================================
    # 🛡️ BULLETPROOF ERROR HANDLING
    # ==========================================
    except APIError as e:
        # This catches EVERYTHING from OpenAI (429, 401, 500, etc.)
        status_code = getattr(e, 'status_code', 'Unknown')
        error_message = getattr(e, 'message', str(e))
        
        if status_code == 429:
            return "⚠️ **API Quota Exceeded:** Your OpenAI API key has run out of credits or hit a rate limit. Please check your billing at platform.openai.com."
        elif status_code == 401:
            return "⚠️ **Authentication Error:** Your OpenAI API key is invalid or missing. Please check your `.env` file."
        else:
            return f"⚠️ **OpenAI API Error (Status {status_code}):** {error_message}"
            
    except Exception as e:
        # This catches SQL syntax errors, database locks, or any other Python errors
        return f"❌ **System Error:** {str(e)}"


# ============================================
# TEST BLOCK (Runs only if you execute this file directly)
# ============================================
if __name__ == "__main__":
    print("🧪 Testing LLM Query Engine...\n")
    test_questions = [
        "How many customers do we have?",
        "What is the most expensive product?",
    ]

    for q in test_questions:
        print(f"\n{'='*60}")
        print(f"❓ Question: {q}")
        print(f"{'='*60}")
        answer = ask_database(q)
        print(f"\n✅ Answer: {answer}")