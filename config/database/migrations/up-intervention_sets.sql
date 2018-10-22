CREATE TABLE intervention_sets(
	"id" serial PRIMARY KEY,
	"sector" integer,
	"name" varchar,
	"description" varchar,
	"interventions" integer[]
);