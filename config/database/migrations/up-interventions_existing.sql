CREATE TABLE interventions_existing(
	"id" serial PRIMARY KEY,
	"intervention_set" integer,
	"intervention_id" integer,
	"intervention_state_id" integer,
	"intervention_type_id" integer,
	"build_date" integer
);