import yaml
from functools import lru_cache

class PromptRegistry:
    def __init__(self, source):
        self.source = source
        self.prompts = self._load()

    @lru_cache
    def _load(self):
        with open(self.source, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get(self, category :str, name : str, version : str = "v1"):
        return self.prompts[category][name][version]