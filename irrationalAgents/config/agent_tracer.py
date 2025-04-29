from langsmith import Client

class AgentTracer:
    def __init__(self):
        self.client = Client()
        self.parent_run = None

    def start_agent_run(self, agent_name, tick_info):
        self.parent_run = self.client.create_run(
            name=f"AgentRun-{agent_name}",
            inputs={"tick_info": tick_info},
            run_type="chain",
        )

    def end_agent_run(self):
        self.parent_run = None  # 释放

    def trace_child_step(self, step_name, inputs, outputs):
        if not self.parent_run:
            raise Exception("Parent run not started!")
        self.client.create_run(
            name=step_name,
            inputs=inputs,
            outputs=outputs,
            run_type="tool",
            parent_run_id=self.parent_run.id
        )
