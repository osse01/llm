from google.adk.agents import LlmAgent  
from google.adk.tools.mcp_tool import MCPToolset
from google.adk.tools.mcp_tool import StdioConnectionParams
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session
from google.adk.memory import InMemoryMemoryService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.agents.run_config import RunConfig
from google.genai import types
from mcp import StdioServerParameters
import requests
from typing import Dict, Any
import json, os, uuid
import logging


class WeatherAgentRunner:
    def __init__(self, app_name, user_id=None, session_id=None):
        self.app_name = app_name
        self.user_id = user_id or str(uuid.uuid4())
        self.session_id = session_id or str(uuid.uuid4())

        self.weather_apis = {
            'YR': 'https://api.met.no/weatherapi/locationforecast/2.0/compact',
            'SMHI': 'https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{lon}/lat/{lat}/data.json'
        }
    async def Init(self):    
        self.session_service = InMemorySessionService()
        session = await  self.session_service.get_session(
            app_name=self.app_name,
            user_id=self.user_id,
            session_id=self.session_id,
        )
        if session is None:
            await self.session_service.create_session(
                app_name=self.app_name,
                user_id=self.user_id,
                session_id=self.session_id
            )

        # TODO: Implement API calls as MCP tools so agent can choose more precisely 
        #       which/what weather data to collect.

        self.agent_tools = []
        
        self.agent = LlmAgent(
            name="Advanced_Weather_Reporter",
            model="gemini-2.0-flash",
            instruction=self._get_agent_instructions(),
            description="An assistant that fetches and analyzes weather data from multiple sources.",
            tools=self.agent_tools
        )

        self.runner = Runner(
            agent=self.agent,
            app_name=self.app_name,
            session_service=self.session_service,
            artifact_service=InMemoryArtifactService(),
            memory_service=InMemoryMemoryService(),
        )
    
    def _get_agent_instructions(self) -> str:
        """Generate comprehensive instructions for the agent"""
        return """
        You are an advanced weather prediction agent with these capabilities:
        1. Fetch weather data from YR and SMHI APIs
        2. Compare predictions from different sources
        3. Provide weather forecasts with confidence levels
        4. Explain weather patterns in simple terms
        
        Always check multiple sources when possible and note any discrepancies.
        """
    
    def get_weather_data(self, source: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch weather data from specified source"""
        try:
            if source == 'SMHI':
                url = self.weather_apis[source].format(
                    lon=params['lon'],
                    lat=params['lat']
                )
                response = requests.get(
                    url,
                    headers={'User-Agent': 'WeatherAgent/1.0'}
                )
            else:
                # Handle other potential APIs that might use query parameters
                response = requests.get(
                    self.weather_apis[source],
                    params=params, # Pass params as a dictionary
                    headers={'User-Agent': 'WeatherAgent/1.0'}
                )

            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def run_weather_query(self, location: str) -> str:
        """Run a complete weather analysis for a location"""
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent=self.app_name)
        location = geolocator.geocode(location)
        parameters = {
            'lat': round(location.latitude,4), 
            'lon': round(location.longitude,4)}
        # parameters = {
        #     'lat': '59.3293',  # Example: Stockholm
        #     'lon': '18.0686'
        # }
        
        # Fetch data from both sources
        yr_data = self.get_weather_data('YR', parameters)
        smhi_data = self.get_weather_data('SMHI', parameters)
        
        # Let the agent analyze and compare
        prompt = f"""
        Analyze and compare these weather reports for {location}:
        
        YR Data: {json.dumps(yr_data, indent=2)}
        SMHI Data : {json.dumps(smhi_data, indent=2)}
        
        Provide a summarized weather forecast for the next 48 hours, 
        noting any significant differences between sources. Answer in just a few lines of text.
        """
        #prompt = """Say hello if you understand me (Debug)"""
        try:
            async for event in self.runner.run_async(
                new_message=types.Content(role='user', parts=[types.Part(text=prompt)]),
                user_id=self.user_id,
                session_id=self.session_id,
                run_config=RunConfig(max_llm_calls=10)
            ):
                if event.is_final_response():
                    if event.content and event.content.parts:
                        final_response = event.content.parts[0].text
        except LlmCallsLimitExceededError:
            self.logger.warning(
                "max_llm_calls reached, ask to finish reasoning, restarting agent cycle..."
            )
        # async for event in response_stream:
        #     if event.content:
        #         full_answer += event.content.parts[0].text
        return final_response