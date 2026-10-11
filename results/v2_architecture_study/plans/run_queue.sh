#!/bin/sh
# Sequential queue: wait for a PID, then run stage 1b and stage 2.
while kill -0 "$1" 2>/dev/null; do sleep 5; done
python3 -u exp2_pipeline.py --plan ../results/v2_architecture_study/plans/stage1b_selv3.json --out exp_s_decision_v3.json > ../results/v2_architecture_study/stage1b.log 2>&1
python3 -u exp2_pipeline.py --plan ../results/v2_architecture_study/plans/stage2_writer.json --out exp_w_writer.json > ../results/v2_architecture_study/stage2.log 2>&1
