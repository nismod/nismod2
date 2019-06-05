#
# Copy subset of results to S3
#
# e.g. usage:
#     bash utilities/copy_results.sh arc_ets__expansion

model_run=$1

aws s3 cp --recursive \
    results/$model_run/convert_units_ed_to_es_constrained/decision_0/ \
    s3://nismod2-arc-results/$model_run/convert_units_ed_to_es_constrained/decision_0/

aws s3 cp --recursive \
    results/$model_run/energy_supply_constrained/decision_0/ \
    s3://nismod2-arc-results/$model_run/energy_supply_constrained/decision_0/

aws s3 cp --recursive \
    results/$model_run/convert_units_tr_to_es/decision_0/ \
    s3://nismod2-arc-results/$model_run/convert_units_tr_to_es/decision_0/
