from langsmith import traceable

def dynamic_traceable(name_func, run_type="chain"):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            name = name_func(self, *args, **kwargs)
            parent_id = kwargs.get("parent_run_id")
            traced = traceable(name=name, run_type=run_type, parent_run_id=parent_id)(method)
            return traced(self, *args, **kwargs)
        return wrapper
    return decorator

