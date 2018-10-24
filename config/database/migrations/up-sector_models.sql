CREATE TABLE sector_models(
	"id" serial PRIMARY KEY,
	"name" varchar,
	"sector_id" integer,
	"description" varchar,
  "path" varchar,
  "initial_conditions" varchar[],
  "inputs" json,
  "interventions" varchar[],
	"outputs" json,
	"parameters" varchar
);