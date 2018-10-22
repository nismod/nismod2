CREATE TABLE sector_model_details(
	"id" serial PRIMARY KEY,
	"name" varchar,
	"sector_model_id" integer,
	"model_version" double precision,
	"run_information" varchar,
	"required_parameters" varchar[],
	"requried_input_datasets" varchar[],
	"output_datasets" varchar[]
);