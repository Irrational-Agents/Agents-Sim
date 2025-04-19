import json
from prompt.llm_command_list import *
from config.logger_config import setup_logger
from config.config import AGENT_BIASES

logger = setup_logger(__name__)

# The environment conditions must be checked to see if they meet the objectives of the plan, employing the item interaction condition logic of the generating agent.
# If the target interaction object is occupied, the agent re-scans until the condition is satisfied. Once the target of the environmental object to execute the plan is secured, the agent takes over the interaction spot (in the case of a social scenario, reserving an adjacent spot for a social peer) and executes the action: continuous development of communication: when two agents are within a certain probability of triggering a dialogue once they are within a distance, depending on their social tendencies and current state (e.g., if the agent's plan is social, it will actively initiate a conversation).


def plan_evaluation(agent, plan_list):
    try:
        if not plan_list or not isinstance(plan_list, list):
            logger.warning("Warning: Plan list is empty or not a list.")
            return None

        # a plan should be evaluated based on bias, Context (in this stage it should be personality)
        p_context = agent.basic_info.get('personality_traits', {})
        basic_needs = agent.short_memory.basic_needs
        best_plan = select_plan(plan_list, p_context,basic_needs,agent.short_memory.recent_events) 
        action = decide_next_action(best_plan)

        return action

    except Exception as e:
        logger.error(f"Error evaluating plans: {str(e)}")
        return plan_list[0]


def select_plan(plan_list, p_context, basic_needs, recent_events):
    # this will return optimal response if no biases else it will send 
    # experimental part
    biases=''
    if AGENT_BIASES:
        #@TODO biases = bias_module(bias)
        biases = ''
    logger.debug(f"biases: {biases} p_context: {p_context}")
    plan = plans_selection(plan_list, p_context, recent_events, basic_needs, biases)
    return plan

def decide_next_action(best_plan):
    # 最適なプランに基づいて次のアクションを決定するロジックをここに実装します
    # 例: プランの'action'フィールドを返す単純な実装
    return best_plan