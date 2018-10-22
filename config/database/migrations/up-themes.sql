CREATE TABLE themes(
	"id" serial PRIMARY KEY,
	"name" varchar,
	"description" varchar,
	"package_ids" int[],
	"visable" boolean	
);