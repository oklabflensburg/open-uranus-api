SET client_encoding = 'UTF8';
SET client_min_messages = warning;

CREATE SCHEMA IF NOT EXISTS uranus;
SET search_path TO uranus, public;


-- POSTGIS ERWEITERUNG LADEN
CREATE EXTENSION IF NOT EXISTS postgis;


-- FUNKTION IM URANUS RAUM
CREATE OR REPLACE FUNCTION update_modified_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.modified_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;



DROP TABLE IF EXISTS uranus.organizer CASCADE;

CREATE TABLE IF NOT EXISTS uranus.organizer (
  id INT NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  contact_email VARCHAR(255),
  contact_phone VARCHAR(50),
  website_url TEXT,
  street VARCHAR(255),
  house_number VARCHAR(50),
  postal_code VARCHAR(20),
  city VARCHAR(100),
  country VARCHAR(100),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
  modified_at TIMESTAMP WITH TIME ZONE
);



DROP TABLE IF EXISTS uranus.venue CASCADE;

CREATE TABLE IF NOT EXISTS uranus.venue (
  id INT NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  organizer_id INTEGER,
  name VARCHAR(255) NOT NULL,
  street VARCHAR(255),
  house_number VARCHAR(50),
  postal_code VARCHAR(20),
  city VARCHAR(100),
  country_code character(3),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
  modified_at TIMESTAMP WITH TIME ZONE,
  wkb_geometry geometry(POINT, 4326) NOT NULL, -- Ensure schema is referenced
  county_code VARCHAR(10),
  opened_at date,
  closed_at date,
  CONSTRAINT country_length_check CHECK ((char_length((country_code)::text) = 3)),
  FOREIGN KEY (organizer_id) REFERENCES uranus.organizer(id)
);



DROP TABLE IF EXISTS uranus.space CASCADE;

CREATE TABLE IF NOT EXISTS uranus.space (
  id INT NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  venue_id INTEGER NOT NULL,
  name VARCHAR(255) NOT NULL,
  total_capacity INTEGER,
  seating_capacity INTEGER,
  space_type_id INTEGER,
  building_level INTEGER,
  platform_lift VARCHAR(255),
  wheelchair TEXT,
  toilets TEXT,
  elevator TEXT,
  ramp TEXT,
  tactile_guidance TEXT,
  accessibility_info TEXT,
  personalized_accessibility_services BOOLEAN,
  wheelchair_friendly_surface TEXT,
  quiet_zones TEXT,
  url TEXT,
  floor_plan TEXT,
  tech_rider TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
  modified_at TIMESTAMP WITH TIME ZONE,
  area NUMERIC,
  FOREIGN KEY (venue_id) REFERENCES uranus.venue(id) ON DELETE CASCADE
);



DROP TABLE IF EXISTS uranus.event CASCADE;

CREATE TABLE IF NOT EXISTS uranus.event (
  id INT NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  organizer_id INTEGER NOT NULL,
  venue_id INTEGER NOT NULL,
  space_id INTEGER,
  title VARCHAR(255) NOT NULL,
  description text NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
  modified_at TIMESTAMP WITH TIME ZONE,
  FOREIGN KEY (space_id) REFERENCES uranus.space(id) ON DELETE SET NULL,
  FOREIGN KEY (organizer_id) REFERENCES uranus.organizer(id) ON DELETE CASCADE,
  FOREIGN KEY (venue_id) REFERENCES uranus.venue(id) ON DELETE CASCADE
);



DROP TABLE IF EXISTS uranus.image CASCADE;

CREATE TABLE IF NOT EXISTS uranus.image (
  id INT NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  name VARCHAR(255) NOT NULL,
  file_name VARCHAR(255) NOT NULL,
  file_type VARCHAR(50),
  license VARCHAR(255),
  created_by VARCHAR(255),
  copyright VARCHAR(255),
  image_type VARCHAR(50),
  tags text[],
  alt_text TEXT,
  caption TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
  modified_at TIMESTAMP WITH TIME ZONE
);



DROP TABLE IF EXISTS uranus.logo CASCADE;

CREATE TABLE IF NOT EXISTS uranus.logo (
  id INT NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  name VARCHAR(255) NOT NULL,
  file_type VARCHAR(50) NOT NULL,
  background_type VARCHAR(50),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
  modified_at TIMESTAMP WITH TIME ZONE
);



DROP TABLE IF EXISTS uranus.transport_station CASCADE;

CREATE TABLE IF NOT EXISTS uranus.transport_station (
  id INT NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  station_type VARCHAR(50) NOT NULL,
  name VARCHAR(255) NOT NULL,
  distance_by_foot INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
  modified_at TIMESTAMP WITH TIME ZONE
);



DROP TABLE IF EXISTS uranus.venue_url CASCADE;

CREATE TABLE IF NOT EXISTS uranus.venue_url (
  id INT NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  venue_id INTEGER NOT NULL,
  link_type VARCHAR(255),
  url text NOT NULL,
  title VARCHAR(255),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
  modified_at TIMESTAMP WITH TIME ZONE,
  FOREIGN KEY (venue_id) REFERENCES uranus.venue(id) ON DELETE CASCADE
);



DROP TABLE IF EXISTS uranus.event_date CASCADE;

CREATE TABLE IF NOT EXISTS uranus.event_date (
  id INT NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  event_id INTEGER NOT NULL,
  venue_id INTEGER NOT NULL,
  space_id INTEGER,
  start_date TIMESTAMP WITH TIME ZONE NOT NULL,
  end_date TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
  modified_at TIMESTAMP WITH TIME ZONE,
  entry_time TIME WITH TIME ZONE,
  FOREIGN KEY (event_id) REFERENCES uranus.event(id) ON DELETE CASCADE,
  FOREIGN KEY (venue_id) REFERENCES uranus.venue(id) ON DELETE CASCADE,
  FOREIGN KEY (space_id) REFERENCES uranus.space(id) ON DELETE SET NULL
);



DROP TABLE IF EXISTS uranus.i18n CASCADE;

CREATE TABLE IF NOT EXISTS uranus.i18n (
  id INT NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  iso_code_alpha_3 VARCHAR(10) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  modified_at TIMESTAMP WITH TIME ZONE
);



DROP TABLE IF EXISTS uranus.space_type CASCADE;

CREATE TABLE IF NOT EXISTS uranus.space_type (
  id INT NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  i18n_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  modified_at TIMESTAMP WITH TIME ZONE,
  FOREIGN KEY (i18n_id) REFERENCES uranus.i18n(id) ON DELETE CASCADE
);



DROP TABLE IF EXISTS uranus.venue_type CASCADE;

CREATE TABLE IF NOT EXISTS uranus.venue_type (
  id INT NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  i18n_id INTEGER NOT NULL,
  type_name TEXT NOT NULL,
  FOREIGN KEY (i18n_id) REFERENCES uranus.i18n(id) ON DELETE CASCADE
);




DROP TABLE IF EXISTS uranus.venue_link_types CASCADE;

CREATE TABLE IF NOT EXISTS uranus.venue_link_types (
  venue_id INTEGER NOT NULL,
  venue_type_id INTEGER NOT NULL,
  PRIMARY KEY (venue_id, venue_type_id),
  FOREIGN KEY (venue_id) REFERENCES uranus.venue(id) ON DELETE CASCADE,
  FOREIGN KEY (venue_type_id) REFERENCES uranus.venue_type(id) ON DELETE CASCADE
);




CREATE TRIGGER set_modified_at BEFORE UPDATE ON uranus.event FOR EACH ROW EXECUTE FUNCTION uranus.update_modified_at();
CREATE TRIGGER set_modified_at BEFORE UPDATE ON uranus.event_date FOR EACH ROW EXECUTE FUNCTION uranus.update_modified_at();
CREATE TRIGGER set_modified_at BEFORE UPDATE ON uranus.image FOR EACH ROW EXECUTE FUNCTION uranus.update_modified_at();
CREATE TRIGGER set_modified_at BEFORE UPDATE ON uranus.logo FOR EACH ROW EXECUTE FUNCTION uranus.update_modified_at();
CREATE TRIGGER set_modified_at BEFORE UPDATE ON uranus.organizer FOR EACH ROW EXECUTE FUNCTION uranus.update_modified_at();
CREATE TRIGGER set_modified_at BEFORE UPDATE ON uranus.space FOR EACH ROW EXECUTE FUNCTION uranus.update_modified_at();
CREATE TRIGGER set_modified_at BEFORE UPDATE ON uranus.space_type FOR EACH ROW EXECUTE FUNCTION uranus.update_modified_at();
CREATE TRIGGER set_modified_at BEFORE UPDATE ON uranus.transport_station FOR EACH ROW EXECUTE FUNCTION uranus.update_modified_at();
CREATE TRIGGER set_modified_at BEFORE UPDATE ON uranus.venue FOR EACH ROW EXECUTE FUNCTION uranus.update_modified_at();
CREATE TRIGGER set_modified_at BEFORE UPDATE ON uranus.venue_type FOR EACH ROW EXECUTE FUNCTION uranus.update_modified_at();
CREATE TRIGGER set_modified_at BEFORE UPDATE ON uranus.venue_url FOR EACH ROW EXECUTE FUNCTION uranus.update_modified_at();
