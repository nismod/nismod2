CREATE TABLE region(
	"id" serial PRIMARY KEY,
	"name" varchar,
	"region_set" int,
	"geometry" geometry,
	"region_type" int	
);