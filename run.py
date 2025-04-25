"""
Main script to run the FastAPI application.
"""
import uvicorn

if __name__ == "__main__":
    # Run the application using Uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
        log_level="info",
    )
