CREATE TABLE packages(
	"id" serial PRIMARY KEY,
	"name" varchar,
	"description" varchar,
	"model_run_ids" int[],
	"visable" boolean	
);