from routes import app

# Start the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)