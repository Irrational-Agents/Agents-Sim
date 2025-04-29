import json
import os
from openai import OpenAI
from langsmith.wrappers import wrap_openai
from langsmith import traceable
from config.config import PROMPT_FILE_PATH
from prompt.prompt_config import PROMPT_CONFIG
from config.logger_config import setup_logger

logger = setup_logger(__name__)
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)


def _load_prompt_files(file_list):
    return [open(PROMPT_FILE_PATH + f, 'r', encoding='utf-8').read() for f in file_list]


def render_prompt(template, variables):
    return template.format(**variables)

@traceable(name='call', run_type='llm')
def call_openai(system_content, user_content, function):
    try:
        chat_kwargs = {
            "model": "gpt-4o-mini-2024-07-18",
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content}
            ]
        }
        if function:
            tools = [{
                "type": "function",
                "function": {
                    **function,
                    "strict": True
                },
            }]
            chat_kwargs["tools"] = tools
            chat_kwargs["tool_choice"] = {
                "type": "function",
                "function": {
                    "name": function["name"]
                }
            }


        completion = client.chat.completions.create(
            **chat_kwargs
        )

        message = completion.choices[0].message
        if function and hasattr(message, "function_call"):
            logger.debug(f"Function call: {getattr(message, 'function_call')}")
            return message.tool_calls[0].function.arguments
        else:
            return message.content
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return None


def run_prompt_task(task_name, agent_tracer=None, **variables):

    config = PROMPT_CONFIG.get(task_name)
    if not config:
        raise ValueError(f"No configuration for task: {task_name}")

    templates = _load_prompt_files(config["files"])
    system_content = config["system"]
    function_schemas = config.get(
        "function_schema", [None for _ in range(len(templates))])
    try:
        for t, function_schema in zip(templates, function_schemas):
            user_prompt = render_prompt(t, variables)
            result = call_openai(system_content, user_prompt, function_schema)
            logger.debug(f"[{task_name}] result: {result}")
            if config["type"] == "json":
                try:
                    result = json.loads(result).get("resp")
                except Exception:
                    logger.error(f"[{task_name}] JSON decoding error: {result}")
                    return None

            if config.get('stream'):
                variables = {**variables, config['stream'][0]: result}  # 先暂时写死
                logger.debug(f"[{task_name}] stream result: {result}")
        
        logger.debug(f"[{task_name}] result: {result}")
        if agent_tracer and agent_tracer.parent_run:
            agent_tracer.trace_child_step(
                step_name=task_name,
                inputs=variables,
                outputs={"result": result}
            )

        return result
    except Exception as e:
        logger.error(f"[{task_name}] error: {str(e)}")
        if agent_tracer and agent_tracer.parent_run:
            agent_tracer.trace_child_step(
                step_name=f"{task_name} [Error]",
                inputs=variables,
                outputs={"error": str(e)}
            )
        return None
