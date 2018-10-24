CREATE TABLE sos_model_runs(
	"id" serial PRIMARY KEY,
	"name" varchar,
	"description" varchar,
	"sos_model" varchar,
	"timesteps" int[] ,
	"strategies" varchar[],
	"scenarios" json,
	"decision_module" varchar,
	"narratives" json,
	"stamp" timestamp
);