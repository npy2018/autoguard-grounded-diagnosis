from pathlib import Path

from autoguard_agent.demo import run

if __name__ == "__main__":
    result = run(Path("outputs/grounded_diagnosis.json"))
    print(result["hypotheses"][0]["statement"])
