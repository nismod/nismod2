-- region tables
ALTER TABLE region DROP CONSTRAINT IF EXISTS region_regionset_fky;
ALTER TABLE region DROP CONSTRAINT IF EXISTS region_regiontype_fky;

-- interval tables
ALTER TABLE intervals DROP CONSTRAINT IF EXISTS intervals_set_fky;