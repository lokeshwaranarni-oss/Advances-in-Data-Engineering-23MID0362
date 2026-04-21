from core.profiler import profile_data
from core.decision_engine import select_best_method
from core.monitoring import monitor_compression
import os
import sys
import traceback

def test():
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    output_dir = os.path.join(data_dir, "compressed")
    test_file = os.path.join(data_dir, "sample_1mb.csv")
    
    try:
        profile = profile_data(test_file)
        print("Profile:")
        print(profile)
        
        decision = select_best_method(profile)
        print("Decision:", decision['method'])
        
        metrics = monitor_compression(test_file, decision['method'], output_dir)
        print("Metrics:", metrics)
    except Exception as e:
        print("Error during execution:", e)
        traceback.print_exc()

if __name__ == "__main__":
    test()
