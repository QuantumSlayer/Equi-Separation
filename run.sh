# optimization
## SGD
CUDA_VISIBLE_DEVICES=0 nohup python representation_dynamics_terminal.py data=cfm model=GFNN layer_num=2 hidden_size=100 measure=within_variance optimization=sgd lr=0.3 > logs/cfm_GFNN_2_100_sgd_within_0.3_terminal.log 2>&1 &
CUDA_VISIBLE_DEVICES=0 nohup python representation_dynamics_terminal.py data=cfm model=GFNN layer_num=6 hidden_size=100 measure=within_variance optimization=sgd lr=0.03 > logs/cfm_GFNN_6_100_sgd_within_0.03_terminal.log 2>&1 &
CUDA_VISIBLE_DEVICES=0 nohup python representation_dynamics_terminal.py data=cfm model=GFNN layer_num=18 hidden_size=100 measure=within_variance optimization=sgd lr=0.01 > logs/cfm_GFNN_18_100_sgd_within_0.01_terminal.log 2>&1 &