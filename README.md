**LLM Agents**

My repo where I play around with MCP and Google ADK.

To get started you need to have a api key. You can generate one for free on Google Cloud.
After that set your environemt variable

> GOOGLE_API_KEY="abcdef"
> GEMINI_API_KEY="abcdef"

On linux you can append them to the .bashrc file:
```bash
echo 'export GOOGLE_API_KEY="abcdef"' >> ~/.bashrc
echo 'export GEMINI_API_KEY="abcdef"' >> ~/.bashrc
```
or add them to your .env file.

On windows you can set the environment variables by searching on that setting.

Run
```bash
pip install adk
```
in the virtual environment.

After that you should be good too go!


**Contents:**

1.  **song-agents:** 

    I tested out the new live music generation feature made by Google.

3.  **weather-agent**

    I tested out an LLM agent to fuse together weather data to predict in a 48h forecast.

