# AI_Frontend_UI_LLM 

<img width="1903" height="915" alt="image" src="https://github.com/user-attachments/assets/cffc0754-665c-4191-a9df-15afcf9d1923" />

Support list 🔥
- Openrouter  https://openrouter.ai/
- ollama  https://ollama.com/
- unsloth  https://unsloth.ai/
- Aion  https://aionui.com/

#### - Frontend ▶️ HTML + BOOTSTRAP

#### - Backend ▶️ Python (API)


## How to start with venv

```
python -m venv venv && venv\Scripts\activate
```

```
uvicorn main:app --reload
```

try open index.html


# How Change Provider 

1. change .env file   use your api key

2. edit main.py

- change base url with your provider

- change API_NAME  With your provider   you can check name in .env file   example OPENROUTER_API_KEY  or OLLAMA_API_KEY

```
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)
```
3. change model selector with your privider model name  example openai/gpt-oss-120b:free  or  unsloth/gpt-oss-120b

```
<select class="model-selector" id="modelSelect">
                <option value="openai/gpt-oss-120b:free">gpt-oss-120b</option>
        </select>
```


#### every change restart backend with  

```
uvicorn main:app --reload
```

🔥🔥🔥🔥
