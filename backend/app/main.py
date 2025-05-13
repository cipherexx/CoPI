import asyncio
import json
import os
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import time
from app.scripts.ambitionbox_scraper import get_ambitionbox_rating
from app.scripts.gnews_fetcher import getGNews
from app.scripts.kanoon_scraper import scrape_indiankanoon
from app.scripts.mouthshut_scraper import scrape_mouthshut, get_mouthshut_url
from app.scripts.pagespeed import fetchPSAnalytics
from app.scripts.twikit_fetcher import fetch_tweets
from app.scripts.yfinance_fetcher import yfinance_full

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

async def run_task(task_name, company_name, func, *args, **kwargs):
    """Run a task and return its result as a JSON string"""
    start_time = time.time()
    try:
        await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
        output_path = kwargs.get("output_json_path", f"{task_name}.json")
        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        result = {
            "task": task_name,
            "status": "success",
            "data": data,
            "time_taken": time.time() - start_time
        }
    except Exception as e:
        result = {
            "task": task_name,
            "status": "error",
            "error": str(e),
            "time_taken": time.time() - start_time
        }
    
    return json.dumps(result) + "\n"

async def generate_company_info(company_name):
    """Generate company information from all sources"""
    print(f"Generating info for company: {company_name}")
    
    tasks = [
        {
            "name": "ambitionbox",
            "func": get_ambitionbox_rating,
            "args": [company_name],
            "kwargs": {"output_json_path": "output/ambitionbox.json"}
        },
        {
            "name": "stock_data",
            "func": lambda: yfinance_full(company_name, output_path="output/yf_stats.json")
        },
        {
            "name": "legal",
            "func": scrape_indiankanoon,
            "args": [company_name, 2],
            "kwargs": {"output_path": "output/kanoon.json"}
        },
        {
            "name": "reviews",
            "func": lambda: scrape_mouthshut(get_mouthshut_url(company_name), 2, "output/mouthshut.json")
        },
        {
            "name": "news",
            "func": getGNews,
            "args": [company_name],
            "kwargs": {"output_json_path": "output/news.json"}
        },
        {
            "name": "pagespeed",
            "func": fetchPSAnalytics,
            "args": [company_name],
            "kwargs": {"output_path": "output/ps_analytics.json"}
        },
        {
            "name": "tweets",
            "func": fetch_tweets,
            "args": [company_name],
            "kwargs": {"output_json_path": "output/tweets.json"}
        }
        
    ]
    
    print(f"Tasks defined: {len(tasks)}")
    
    # Run tasks concurrently and yield results as they complete
    yield json.dumps({"event": "start", "tasks_count": len(tasks)}) + "\n"
    
    # Process each task
    for task in tasks:
        try:
            task_name = task["name"]
            func = task["func"]
            args = task.get("args", [])
            kwargs = task.get("kwargs", {})
            
            print(f"Processing task: {task_name}")
            
            if asyncio.iscoroutinefunction(func):
                # For async functions
                start_time = time.time()
                try:
                    await func(*args, **kwargs)
                    output_path = kwargs.get("output_json_path", kwargs.get("output_path", f"output/{task_name}.json"))
                    with open(output_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    result = {
                        "task": task_name,
                        "status": "success",
                        "data": data,
                        "time_taken": time.time() - start_time
                    }
                except Exception as e:
                    print(f"Error in async task {task_name}: {str(e)}")
                    result = {
                        "task": task_name,
                        "status": "error",
                        "error": str(e),
                        "time_taken": time.time() - start_time
                    }
                
                yield json.dumps(result) + "\n"
            else:
                # For sync functions
                def run_sync_task():
                    start_time = time.time()
                    try:
                        if callable(func):
                            func(*args, **kwargs)
                        output_path = kwargs.get("output_json_path", kwargs.get("output_path", f"output/{task_name}.json"))
                        with open(output_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        
                        return {
                            "task": task_name,
                            "status": "success",
                            "data": data,
                            "time_taken": time.time() - start_time
                        }
                    except Exception as e:
                        print(f"Error in sync task {task_name}: {str(e)}")
                        return {
                            "task": task_name,
                            "status": "error",
                            "error": str(e),
                            "time_taken": time.time() - start_time
                        }
                
                result = await asyncio.to_thread(run_sync_task)
                yield json.dumps(result) + "\n"
        except Exception as e:
            print(f"Error processing task {task.get('name', 'unknown')}: {str(e)}")
            yield json.dumps({
                "task": task.get("name", "unknown"),
                "status": "error",
                "error": f"Task execution error: {str(e)}"
            }) + "\n"
    
    yield json.dumps({"event": "end"}) + "\n"



@app.get("/api/company/{company_name}")
async def get_company_info(company_name: str):
    """Stream company information as it becomes available"""
    return StreamingResponse(
        generate_company_info(company_name),
        media_type="text/event-stream"
    )
