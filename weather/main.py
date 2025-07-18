import asyncio
from WeatherAgentRunner import WeatherAgentRunner


async def main():
    agent = WeatherAgentRunner(app_name="WeatherAgentApp")
    await agent.Init()
    location =  input("Where do you want your forecast?\n")
    answer = await agent.run_weather_query(location)
    print(answer)

if __name__ == "__main__":
    asyncio.run(main())