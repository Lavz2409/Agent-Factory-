from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import input_analyzer, market_research, competitor_analysis, positioning, use_case, marketing_strategy, campaign_generator, growth_hacking, swot_analysis, final_report_compiler

app = FastAPI(
    title="TraceAI",
    description="An AI-powered platform to help locate missing children using facial recognition and real-time alerts.",
    version="1.0.0"
)

# CORS settings
origins = [
    "http://localhost",
    "http://localhost:8000",
    # Add more origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers for different agents
app.include_router(input_analyzer.router, prefix="/input-analyzer", tags=["Input Analyzer"])
app.include_router(market_research.router, prefix="/market-research", tags=["Market Research"])
app.include_router(competitor_analysis.router, prefix="/competitor-analysis", tags=["Competitor Analysis"])
app.include_router(positioning.router, prefix="/positioning", tags=["Positioning"])
app.include_router(use_case.router, prefix="/use-case", tags=["Use Case"])
app.include_router(marketing_strategy.router, prefix="/marketing-strategy", tags=["Marketing Strategy"])
app.include_router(campaign_generator.router, prefix="/campaign-generator", tags=["Campaign Generator"])
app.include_router(growth_hacking.router, prefix="/growth-hacking", tags=["Growth Hacking"])
app.include_router(swot_analysis.router, prefix="/swot-analysis", tags=["SWOT Analysis"])
app.include_router(final_report_compiler.router, prefix="/final-report", tags=["Final Report Compiler"])

def start_application():
    # This function can be used to initialize resources, databases, etc.
    pass

if __name__ == "__main__":
    import uvicorn
    start_application()
    uvicorn.run(app, host="0.0.0.0", port=8000)