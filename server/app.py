import uvicorn

# This acts as an entry point for OpenEnv validation
def run():
    uvicorn.run("app:app", host="0.0.0.0", port=7860, reload=False)

if __name__ == "__main__":
    run()
