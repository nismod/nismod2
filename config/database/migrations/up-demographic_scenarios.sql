CREATE TABLE demographic_scenarios(
	"id" serial PRIMARY KEY,
	"name" varchar,
	"description" varchar,
	"dataset_id" integer,
	"active" boolean
);