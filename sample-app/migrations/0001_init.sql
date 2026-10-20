-- 0001: initial schema. Do not edit; add a new migration instead.
CREATE TABLE customers (id TEXT PRIMARY KEY, name TEXT NOT NULL, tz TEXT NOT NULL);
CREATE TABLE invoices (id TEXT PRIMARY KEY, customer_id TEXT NOT NULL, amount_cents INTEGER NOT NULL);
