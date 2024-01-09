from routes import app
import uvicorn

# Start the server
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)