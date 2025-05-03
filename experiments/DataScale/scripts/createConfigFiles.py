import yaml
import os

# Base configuration from existing file
base_config_path = "../../../FedBiscuit/fedbiscuit_script/tldr/tldr_choice_llama3.2-3B_ml4ed.yaml"
with open(base_config_path, 'r') as f:
    base_config = yaml.safe_load(f)

# Define data size percentages to experiment with
data_sizes = [round(x * 0.1, 1) for x in range(1, 11)]  # 0.1 to 1.0

# Output directory
output_dir = "../../../FedBiscuit/fedbiscuit_script/tldr/data_size_experiments/"
os.makedirs(output_dir, exist_ok=True)

# Create a config file for each data size
for size in data_sizes:
    # Clone the base config
    config = base_config.copy()
    
    # Update the config with data size specific settings
    config['data']['train_size'] = size  # Add this parameter
    
    # Update paths to save models separately
    size_str = str(int(size * 100))
    config['federate']['save_to'] = f"checkpoints/tldr_choice_gemma_fedbiscuit_u3_data{size_str}pct.ckpt"
    config['expname'] = f"tldr/choice_gemma/data{size_str}pct"
    
    # Save the modified config
    output_path = os.path.join(output_dir, f"tldr_choice_llama3.2-3B_ml4ed_data{size_str}pct.yaml")
    with open(output_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print(f"Created config for {size*100}% data: {output_path}")
