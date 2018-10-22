CREATE TABLE sos_models(
	"id" serial PRIMARY KEY,
	"name" varchar,
	"description" varchar,
	"sector_models" varchar[],
	"dependencies" json,
	"narrative_sets" varchar[],
	"scenario_sets" varchar[],
	"max_iterations" integer,
	"convergence_absolute_tolerance" double precision,
	"convergence_relative_tolerance" double precision
);