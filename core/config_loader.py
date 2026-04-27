import configparser
from pathlib import Path

class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        config_path = Path(__file__).parent.parent / "config" / "orchestrator.conf"
        
        # Valores por defecto
        self.streaming = True
        self.terminal_emulator = "terminator"
        self.use_caveman = True
        self.use_cavemem = True
        self.ollama_url = "http://localhost:11434/api/generate"
        self.capability_map = {
            "code": ["qwen2.5-coder:7b", "moa-master"],
            "reasoning": ["phi4", "moa-master"],
            "chat": ["llama3.1:8b", "moa-master"]
        }
        self.external_keys = {}

        if config_path.exists():
            self.config.read(config_path)
            
            if 'UI' in self.config:
                self.streaming = self.config['UI'].getboolean('streaming', True)
                self.terminal_emulator = self.config['UI'].get('terminal_emulator', 'terminator')
            
            if 'MEMORY' in self.config:
                self.use_caveman = self.config['MEMORY'].getboolean('use_caveman', True)
                self.use_cavemem = self.config['MEMORY'].getboolean('use_cavemem', True)
                
            if 'OLLAMA' in self.config:
                self.ollama_url = self.config['OLLAMA'].get('base_url', self.ollama_url)

            if 'MODELS' in self.config:
                for task in self.config['MODELS']:
                    models_str = self.config['MODELS'].get(task, "")
                    self.capability_map[task] = [m.strip() for m in models_str.split(",") if m.strip()]

            if 'EXTERNAL_API' in self.config:
                for key in self.config['EXTERNAL_API']:
                    self.external_keys[key] = self.config['EXTERNAL_API'].get(key, "")

# Singleton
settings = Config()
