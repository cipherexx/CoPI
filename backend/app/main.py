import asyncio
import json
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import time

# Import the new functions from your updated scripts
from app.scripts.new_finance import analyze_company
from app.scripts.gnews_fetcher import fetch_news_rating
from app.scripts.mouthshut_scraper import mouthshut_fetch
from app.scripts.kanoon_scraper import fetch_indiankanoon_final
from app.scripts.ambitionbox_scraper import get_ambitionbox_rating

app = FastAPI(title="Project X-Ray")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("output", exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Welcome to Project X-Ray"}

async def generate_company_info(company_name):
    """Generate company information from all sources"""
    print(f"Generating info for company: {company_name}")
    
    # Define tasks in the specified order
    tasks = [
        {
            "name": "finance",
            "func": analyze_company,
            "args": [company_name]
        },
        {
            "name": "news",
            "func": fetch_news_rating,
            "args": [company_name]
        },
        {
            "name": "legal",
            "func": fetch_indiankanoon_final,
            "args": [company_name]
        },
        {
            "name": "ambitionbox",
            "func": get_ambitionbox_rating,
            "args": [company_name]
        },
        {
            "name": "reviews",
            "func": mouthshut_fetch,
            "args": [company_name]
        }
    ]
    
    print(f"Tasks defined: {len(tasks)}")
    
    # Signal the start of the process
    yield json.dumps({"event": "start", "tasks_count": len(tasks)}) + "\n"
    
    # Process each task
    for task in tasks:
        try:
            task_name = task["name"]
            func = task["func"]
            args = task.get("args", [])
            
            print(f"Processing task: {task_name}")
            
            # Execute the task
            start_time = time.time()
            try:
                # Handle both synchronous and asynchronous functions
                if asyncio.iscoroutinefunction(func):
                    data = await func(*args)
                else:
                    data = await asyncio.to_thread(func, *args)
                
                # For functions that return JSON strings, parse them
                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                    except json.JSONDecodeError:
                        # If it's not valid JSON, keep as is
                        pass
                
                result = {
                    "task": task_name,
                    "status": "success",
                    "data": data,
                    "time_taken": time.time() - start_time
                }
            except Exception as e:
                print(f"Error in task {task_name}: {str(e)}")
                result = {
                    "task": task_name,
                    "status": "error",
                    "error": str(e),
                    "time_taken": time.time() - start_time
                }
            
            yield json.dumps(result) + "\n"
            
        except Exception as e:
            print(f"Error processing task {task.get('name', 'unknown')}: {str(e)}")
            yield json.dumps({
                "task": task.get("name", "unknown"),
                "status": "error",
                "error": f"Task execution error: {str(e)}"
            }) + "\n"
    
    # Signal the end of the process
    yield json.dumps({"event": "end"}) + "\n"

@app.get("/api/company/{company_name}")
async def get_company_info(company_name: str):
    """Stream company information as it becomes available"""
    return StreamingResponse(
        generate_company_info(company_name),
        media_type="text/event-stream"
    )
