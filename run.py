# main.py
import uvicorn

HOST_NAME = "127.0.0.1"
PORT = 8080

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=HOST_NAME, port=PORT, reload=True)
