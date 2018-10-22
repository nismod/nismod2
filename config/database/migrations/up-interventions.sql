CREATE TABLE interventions(
	"id" serial PRIMARY KEY,
	"name" varchar,
	"intervention_type_id" integer,
	"sector" integer,
	"sector_model" integer,
	"details" varchar
);