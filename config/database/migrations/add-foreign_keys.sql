-- region tables
ALTER TABLE region ADD CONSTRAINT region_regionset_fky FOREIGN KEY (region_set) REFERENCES region_sets (id);

ALTER TABLE region ADD CONSTRAINT region_regiontype_fky FOREIGN KEY (region_type) REFERENCES region_types (id);

-- interval tables

ALTER TABLE intervals ADD CONSTRAINT intervals_set_fky FOREIGN KEY (set) REFERENCES interval_sets (id);
