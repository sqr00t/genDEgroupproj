-- REDSHIFT DDL --

-- Read 5.8.3. The Schema Search Path: https://www.postgresql.org/docs/9.6/ddl-schemas.html
CREATE SCHEMA testschema;
SET search_path TO testschema;

-- Creates stores table
CREATE TABLE "stores"(
    "store_id" CHAR(16) NOT NULL,
    "store_name" VARCHAR(255) NOT NULL,
    PRIMARY KEY ("store_id")
);

-- Creates orders table
CREATE TABLE "orders"(
    "order_id" CHAR(16) NOT NULL,
    "timestamp" TIMESTAMP NOT NULL,
    "store_id" CHAR(16) NOT NULL,
    "total_price" DOUBLE PRECISION NOT NULL,
    "payment_type" CHAR(4) NOT NULL,
    "opt: hash customer name" CHAR(16) NULL,
    "opt: hash card info" CHAR(16) NULL,
    PRIMARY KEY ("order_id"),
    FOREIGN KEY ("store_id") REFERENCES testschema.stores("store_id")
);

-- Creates products table
CREATE TABLE "products"(
    "product_id" CHAR(16) NOT NULL,
    "item_name" VARCHAR(255) NOT NULL,
    "item_size" VARCHAR(255) NOT NULL,
    "item_price" DOUBLE PRECISION NOT NULL,
    PRIMARY KEY ("product_id")
);

-- Creates orders_products table
CREATE TABLE "orders_products"(
    "order_id" CHAR(16) NOT NULL,
    "product_id" CHAR(16) NOT NULL,
    "quantity" INTEGER NOT NULL,
    PRIMARY KEY ("order_id", "product_id"),
    FOREIGN KEY ("order_id") REFERENCES testschema.orders("order_id"),
    FOREIGN KEY ("product_id") REFERENCES testschema.products("product_id")
);

-- Comments
COMMENT
ON COLUMN
    testschema.orders."order_id" IS 'Hash the concatenated result of string of values in a row as unique ID. Use SHA256(or 512).';
COMMENT
ON COLUMN
    testschema.orders."payment_type" IS 'char(4)';
COMMENT
ON COLUMN
    testschema.orders."opt: hash customer name" IS 'char(16)';
COMMENT
ON COLUMN
    testschema.orders."opt: hash card info" IS 'char(16)';
COMMENT
ON COLUMN
    testschema.orders."timestamp" IS 'Check pgsql timestamp formatting';
COMMENT
ON COLUMN
    testschema.products."product_id" IS 'Hash the concatenated result of string of values in a ​row as unique ID. Use SHA256(or 512)';
COMMENT
ON COLUMN
    testschema.orders_products."quantity" IS 'aggregate of item_count where order_id and product_id';