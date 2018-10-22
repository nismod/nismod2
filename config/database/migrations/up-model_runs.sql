CREATE TABLE model_runs(
	"id" serial PRIMARY KEY,
	"timesteps" varchar,
	"sector_models" varchar,
	"region_sets" integer,
	"interval_sets" integer,
	"scenario" integer,
	"smif_version_id" integer,
	"initial_intervention_set" integer,
	"planned_intervention_set" integer,
	"start_run_time" timestamp,
	"end_run_time" timestamp,
	"total_run_time" double precision,
	"state" integer
);