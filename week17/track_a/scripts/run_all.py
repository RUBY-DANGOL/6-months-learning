from churn_mlops.monitoring import run_monitoring
from churn_mlops.training import run_training

if __name__ == "__main__":
    print("Training and registering candidate models...")
    print(run_training())
    print("Generating and logging drift evidence...")
    print(run_monitoring())

