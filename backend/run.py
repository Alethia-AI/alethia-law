# main.py
import uvicorn

import nest_asyncio
nest_asyncio.apply()

HOST_NAME = "127.0.0.1"#"0.0.0.0"
PORT = 5001

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=HOST_NAME, port=PORT, reload=True)
