### Summary of the Guide
This blog post, authored by Bonnie and Nathan Tarbert on September 25, 2025, serves as a quickstart tutorial for integrating Agent Development Kit (ADK) agents with a frontend using the AG-UI Protocol and CopilotKit. It focuses on creating a full-stack AI agent setup where ADK handles the backend AI logic, AG-UI bridges communication between frontend and backend, and CopilotKit powers the interactive frontend UI. The guide assumes basic knowledge of React/Next.js and Python.

Key benefits highlighted:
- ADK simplifies building production-ready AI agents with planning, tool use, and state management.
- AG-UI enables real-time, event-based interactions.
- CopilotKit allows easy integration of AI chatbots, agents, and generative UI in React apps.

The tutorial includes a preview of a chatbot that can set themes, generate proverbs, and fetch weather. It provides step-by-step instructions with code snippets for setup, backend integration, and frontend building. This can be directly adapted for your project to create interactive AI agents.

### What is the Agent Development Kit (ADK)?
ADK is an open-source framework for building complex AI agents. Core features:
- **Planning**: Multi-step reasoning and execution.
- **Tool Use**: Integration with APIs, services, and data sources.
- **State Management**: Automates chaining logic and progress tracking.

It allows rapid prototyping while offering customization. For more details, refer to the ADK docs (linked in the post).

### Prerequisites
To follow the guide:
- Basic understanding of React or Next.js.
- Python installed (for backend).
- AG-UI Protocol: Open-source protocol for frontend-backend AI interactions (GitHub: https://github.com/AG-UI/ag-ui).
- Gemini API Key: From https://makersuite.google.com/app/apikey (for powering ADK agents with Gemini models).
- CopilotKit: Framework for building AI chatbots and agents (GitHub: https://github.com/CopilotKit/copilotkit).

### Setting Up a Full-Stack ADK Agent Using CLI
This section uses a CLI to scaffold a project with ADK backend, AG-UI integration, and CopilotKit frontend.

1. **Run CLI Command**:
   - If no existing ADK agent, run: `npx copilotkit@latest create -f adk`
   - Provide a project name when prompted.

2. **Install Dependencies**:
   - Use your package manager (e.g., `pnpm install`, `npm install`, etc.).

3. **Configure Gemini API Key**:
   - Create a `.env` file in the root: `GOOGLE_API_KEY="your-google-api-key-here"`.

4. **Run Development Server**:
   - Start with `pnpm dev` (or equivalent).
   - Access at http://localhost:3000.
   - Test tools like setting themes, writing proverbs, or getting weather.

This sets up a basic chatbot integrated with ADK.

### Integrating ADK Agent with AG-UI Protocol in the Backend
This covers wrapping an ADK agent with AG-UI for frontend exposure via an ASGI app (using FastAPI).

1. **Install AG-UI Package**:
   - Run: `pip install ag_ui_adk uvicorn fastapi`.

2. **Configure Your ADK Agent** (in `./agent.py`):
   - Import ADK components and define the agent:
     ```python:disable-run
     from google.adk.agents import LlmAgent
     from google.adk.agents.callback_context import CallbackContext
     from google.adk.sessions import InMemorySessionService, Session
     from google.adk.runners import Runner
     from google.adk.events import Event, EventActions
     from google.adk.tools import FunctionTool, ToolContext
     from google.genai.types import Content, Part, FunctionDeclaration
     from google.adk.models import LlmResponse, LlmRequest
     from google.genai import types
     # ... (other imports as needed)

     proverbs_agent = LlmAgent(
         name="ProverbsAgent",
         model="gemini-2.5-flash",
         instruction="""
         When a user asks you to do anything regarding proverbs, you MUST use the set_proverbs tool.

         IMPORTANT RULES ABOUT PROVERBS AND THE SET_PROVERBS TOOL:
         1. Always use the set_proverbs tool for any proverbs-related requests
         2. Always pass the COMPLETE LIST of proverbs to the set_proverbs tool. If the list had 5 proverbs and you removed one, you must pass the complete list of 4 remaining proverbs.
         3. You can use existing proverbs if one is relevant to the user's request, but you can also create new proverbs as required.
         4. Be creative and helpful in generating complete, practical proverbs
         5. After using the tool, provide a brief summary of what you created, removed, or changed.

         Examples of when to use the set_proverbs tool:
         - "Add a proverb about soap" → Use the tool with an array containing the existing list of proverbs with the new proverb about soap at the end.
         - "Remove the first proverb" → Use a tool with an array containing all of the existing proverbs except the first one.
         - "Change any proverbs about cats to mention that they have 18 lives." → If no proverbs mention cats, do not use the tool. If one or more proverbs mention cats, change them to mention cats having 18 lives, and use the tool with an array of all of the proverbs, including ones that were changed and ones that did not require changes.

         Do your best to ensure proverbs plausibly make sense.

         IMPORTANT RULES ABOUT WEATHER AND THE GET_WEATHER TOOL:
         1. Only call the get_weather tool if the user asks you for the weather in a given location.
         2. If the user does not specify a location, you can use the location "Everywhere ever in the whole wide world"

         Examples of when to use the get_weather tool:
         - "What's the weather today in Tokyo?" → Use the tool with the location "Tokyo"
         - "What's the weather right now?" → Use the location "Everywhere ever in the whole wide world"
         - "Is it raining in London?" → Use the tool with the location "London"
         """,
         tools=[set_proverbs, get_weather],  # Define these tools separately
         before_agent_callback=on_before_agent,
         before_model_callback=before_model_modifier,
         after_model_callback=simple_after_model_modifier
     )
     ```
   - Note: Tools like `set_proverbs` and `get_weather` need to be defined (not fully shown in the post, but implied as custom functions).

3. **Create ADK Middleware Agent Instance** (in `./agent.py`):
   ```python
   from ag_ui_adk import ADKAgent
   # ...

   adk_proverbs_agent = ADKAgent(
       adk_agent=proverbs_agent,
       app_name="proverbs_app",
       user_id="demo_user",
       session_timeout_seconds=3600,
       use_in_memory_services=True
   )
   ```

4. **Configure FastAPI Endpoint**:
   ```python
   from fastapi import FastAPI
   from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint

   app = FastAPI(title="ADK Middleware Proverbs Agent")
   add_adk_fastapi_endpoint(app, adk_proverbs_agent, path="/")

   if __name__ == "__main__":
       import os
       import uvicorn
       if not os.getenv("GOOGLE_API_KEY"):
           print("⚠️  Warning: GOOGLE_API_KEY environment variable not set!")
           print("   Set it with: export GOOGLE_API_KEY='your-key-here'")
           print("   Get a key from: https://makersuite.google.com/app/apikey")
           print()
       port = int(os.getenv("PORT", 8000))
       uvicorn.run(app, host="0.0.0.0", port=port)
   ```
   - Agent available at http://localhost:8000 (or custom port).

### Building a Frontend for Your ADK + AG-UI Agent Using CopilotKit
This uses React/Next.js with CopilotKit for UI.

1. **Install CopilotKit Packages**:
   - Run: `npm install @copilotkit/react-ui @copilotkit/react-core @copilotkit/runtime`.

2. **Set Up Copilot Runtime Instance** (in `/api/copilotkit` API route):
   ```typescript
   import {
     CopilotRuntime,
     ExperimentalEmptyAdapter,
     copilotRuntimeNextJSAppRouterEndpoint,
   } from "@copilotkit/runtime";
   import { HttpAgent } from "@ag-ui/client";
   import { NextRequest } from "next/server";

   const serviceAdapter = new ExperimentalEmptyAdapter();
   const runtime = new CopilotRuntime({
     agents: {
       my_agent: new HttpAgent({
         url: "http://localhost:8000/",
       }),
     },
   });

   export const POST = async (req: NextRequest) => {
     const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
       runtime,
       serviceAdapter,
       endpoint: "/api/copilotkit",
     });
     return handleRequest(req);
   };
   ```

3. **Set Up CopilotKit Provider** (in `layout.tsx`):
   ```typescript
   import type { Metadata } from "next";
   import { CopilotKit } from "@copilotkit/react-core";
   import "./globals.css";
   import "@copilotkit/react-ui/styles.css";

   export const metadata: Metadata = {
     title: "Create Next App",
     description: "Generated by create next app",
   };

   export default function RootLayout({
     children,
   }: Readonly<{
     children: React.ReactNode;
   }>) {
     return (
       <html lang="en">
         <body className={"antialiased"}>
           <CopilotKit runtimeUrl="/api/copilotkit" agent="my_agent">
             {children}
           </CopilotKit>
         </body>
       </html>
     );
   }
   ```

4. **Set Up a Copilot UI Component** (in `page.tsx`):
   ```typescript
   "use client";
   import { CopilotKitCSSProperties, CopilotSidebar } from "@copilotkit/react-ui";
   import { useState } from "react";

   export default function CopilotKitPage() {
     const [themeColor, setThemeColor] = useState("#6366f1");
     // ...

     return (
       <main style={{ "--copilot-kit-primary-color": themeColor } as CopilotKitCSSProperties}>
         <YourMainContent themeColor={themeColor} />
         <CopilotSidebar
           clickOutsideToClose={false}
           defaultOpen={true}
           labels={{
             title: "Popup Assistant",
             initial: "👋 Hi, there! You're chatting with an agent. This agent comes with a few tools to get you started.\n\nFor example you can try:\n- Frontend Tools: \"Set the theme to orange\"\n- Shared State: \"Write a proverb about AI\"\n- Generative UI: \"Get the weather in SF\"\n\nAs you interact with the agent, you'll see the UI update in real-time to reflect the agent's state, tool calls, and progress."
           }}
         />
       </main>
     );
   }
   ```

5. **Sync ADK Agent State with Frontend** (using hooks in `YourMainContent` component):
   - Use `useCoAgent` for bidirectional state sharing.
     ```typescript
     "use client";
     import { useCoAgent } from "@copilotkit/react-core";

     type AgentState = {
       proverbs: string[];
     }

     function YourMainContent({ themeColor }: { themeColor: string }) {
       const { state, setState } = useCoAgent<AgentState>({
         name: "my_agent",
         initialState: {
           proverbs: [
             "CopilotKit may be new, but it's the best thing since sliced bread.",
           ],
         },
       });
       // ... (render UI based on state)
     }
     ```
   - For generative UI (e.g., weather tool):
     ```typescript
     import { useCoAgent, useCopilotAction } from "@copilotkit/react-core";

     // In YourMainContent:
     useCopilotAction({
       name: "get_weather",
       description: "Get the weather for a given location.",
       available: "disabled",
       parameters: [
         { name: "location", type: "string", required: true },
       ],
       render: ({ args }) => {
         return <WeatherCard location={args.location} themeColor={themeColor} />;
       },
     });
     ```
     - Note: Define `<WeatherCard>` as a custom component.

6. **Stream ADK Agent Responses in Frontend**:
   - Pass state to UI components for real-time updates.
     ```typescript
     // In YourMainContent return:
     return (
       <div
         style={{ backgroundColor: themeColor }}
         className="h-screen w-screen flex justify-center items-center flex-col transition-colors duration-300"
       >
         <div className="bg-white/20 backdrop-blur-md p-8 rounded-2xl shadow-xl max-w-2xl w-full">
           <h1 className="text-4xl font-bold text-white mb-2 text-center">Proverbs</h1>
           <p className="text-gray-200 text-center italic mb-6">This is a demonstrative page, but it could be anything you want! 🪁</p>
           <hr className="border-white/20 my-6" />
           <div className="flex flex-col gap-3">
             {state.proverbs?.map((proverb, index) => (
               <div
                 key={index}
                 className="bg-white/15 p-4 rounded-xl text-white relative group hover:bg-white/20 transition-all"
               >
                 <p className="pr-8">{proverb}</p>
                 <button
                   onClick={() => setState({
                     ...state,
                     proverbs: state.proverbs?.filter((_, i) => i !== index),
                   })}
                   className="absolute right-3 top-3 opacity-0 group-hover:opacity-100 transition-opacity bg-red-500 hover:bg-red-600 text-white rounded-full h-6 w-6 flex items-center justify-center"
                 >
                   ✕
                 </button>
               </div>
             ))}
           </div>
           {state.proverbs?.length === 0 && <p className="text-center text-white/80 italic my-8">
             No proverbs yet. Ask the assistant to add some!
           </p>}
         </div>
       </div>
     );
     ```
   - This streams updates like new proverbs in real-time.

### Conclusion and Additional Resources
The guide emphasizes CopilotKit's versatility for AI chatbots and agentic apps. For your project:
- Adapt the CLI for quick prototyping.
- Customize tools and instructions in ADK for specific use cases.
- Extend frontend with more CopilotKit components (e.g., CopilotPopup, CopilotChat).
- Follow CopilotKit on Twitter or join their Discord for community support.

Related posts mentioned:
- "How to Make Agents Talk to Each Other (and Your App) Using A2A + AG-UI" (October 9, 2025).
- "Build a Stock Portfolio AI Agent (Fullstack, Pydantic AI + AG-UI)" (October 3, 2025).
- "Here's How To Build Fullstack Agent Apps (Gemini, CopilotKit & LangGraph)" (September 23, 2025).

This setup can be scaled for your project by replacing example tools (e.g., proverbs, weather) with your own APIs or logic. If integrating with existing code, ensure API keys and ports match.
```