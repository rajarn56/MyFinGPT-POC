# Notes 

## Build fictitous requirement to AI agent capabilities 

I am trying to build agent for practice of implementing AI agent. Lets hypothetically call it as MyFinGPT. Concept that I would like to cover and solidify with implementation are 
- Multiple agents (for eg: Research agent, analyst agent, reporting agent) 
- Integrating with MCP servers
- There can be multiple of these agents with specific purpose and performing them
- Build use case in such a way agent running and parallel and sequence both are covered
- These agents should be able to share context 
- Some agents should perform deductions based on facts, some should analyze sentiment, trends and suggestions
- Functionlity like comparision and provide suggesstion and guidance
- Usage of vector database
- All responses should be grounded and reference should be provided 
- If possible, it should be able to measure tokens used
- Detail out UI that can be used for this with what all information will be shown as result. 
    - It can have panel where use can ask
    - Another section that will give all information, analaysis and report. THis can have trend graph also.

Some technical considerations 
- As this is only hypothetical and poc that has no commercial intention. It is purely to understand agent implementation. Would want to use free resources (APIs and library) that agents can access for getting information like stock, news analysis and so on. Some examples yahoo finance, Alpha vantage, Financial Modeling Prep (FMP)
- Use opensource library like langchain, langgraph and langsmith
- Choose UI implemenation option that is simple to build and understand. 

Understand the above scenario and clearly build requirement and flow. Create this document under 