import uvicorn
import os

port = os.getenv("PORT", 8000)
port=int(port)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
