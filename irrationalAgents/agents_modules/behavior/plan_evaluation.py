import json
from prompt.llm_command_list import *
from config.logger_config import setup_logger
from config.config import AGENT_BIASES

logger = setup_logger(__name__)

# 環境条件が計画の目的を満たしているかどうかを、生成エージェントのアイテム相互作用条件ロジックを採用してチェックしなければならない。
# ターゲットとなる相互作用オブジェクトが占有されている場合、エージェントは条件が満たされるまで再走査する。計画を実行するための環境オブジェクトのターゲットが確保されると、エージェントは相互作用スポットを引き継ぎ（ソーシャルシナリオの場合、ソーシャル仲間のために隣接スポットを予約する）、アクションを実行する： コミュニケーションの継続的発展：2つのエージェントが一定の距離内に入ると、その社会的傾向や現在の状態に応じて、対話が誘発される確率がある（例えば、エージェントのプランが社会的なものであれば、積極的に会話を開始する）。
def plan_evaluation(agent, plan_list):
    try:
        if not plan_list or not isinstance(plan_list, list):
            logger.warning("Warning: Plan list is empty or not a list.")
            return None

        # ここでプランの評価ロジックを実装します
        # 例: 最初のプランを選択する単純な実装
        # a plan should be evaluated based on bias, Context (in this stage it should be personality)
        p_context = agent.basic_info.get('personality_traits', {})
        best_plan = select_plan(plan_list, p_context, agent.short_memory.recent_events) 
        action = decide_next_action(best_plan)

        return action

    except Exception as e:
        logger.error(f"Error evaluating plans: {str(e)}")
        return plan_list[0]


def select_plan(plan_list, p_context, recent_events):
    # this will return optimal response if no biases else it will send 
    # experimental part
    biases=''
    if AGENT_BIASES:
        #@TODO biases = bias_module(bias)
        biases = ''
    logger.debug(f"biases: {biases} p_context: {p_context}, recent events: {recent_events}")
    plan = plans_selection(plan_list, p_context, recent_events, biases)
    return plan

def decide_next_action(best_plan):
    # 最適なプランに基づいて次のアクションを決定するロジックをここに実装します
    # 例: プランの'action'フィールドを返す単純な実装
    return best_plan