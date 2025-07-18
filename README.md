**LLM Agents**

My repo where I play around with MCP and Google ADK.

To get started you need to have a api key. You can generate one for free on Google Cloud.
After that set your environemt variable

> GOOGLE_API_KEY="abcdef"
> GEMINI_API_KEY="abcdef"

On linux you can for example append them to your .bashrc file:
```bash
echo 'export GOOGLE_API_KEY="abcdef"' >> ~/.bashrc
echo 'export GEMINI_API_KEY="abcdef"' >> ~/.bashrc
```
or add them to your .env file.

On windows you can set the environment variables by going to Settings > System > About > Advanced system settings. Click **Environment Variables** where you can add them.


To install the dependencies,

Run
```bash
pip install adk
pip install mcp
```
in the virtual environment.

After that you should be good too go!


**Contents:**

1.  **song-agents:** 

    I tested out the new live music generation feature made by Google.

3.  **weather-agent**

    I tested out an LLM agent to fuse together weather data to predict in a 48h forecast.

