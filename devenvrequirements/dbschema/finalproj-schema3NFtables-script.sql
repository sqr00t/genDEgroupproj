-- Creates stores table
CREATE TABLE "stores"(
    "store_id" BYTEA NOT NULL,
    "store_name" VARCHAR(255) NOT NULL,
    PRIMARY KEY ("store_id")
);

-- Creates orders table
CREATE TABLE "orders"(
    "order_id" BYTEA NOT NULL,
    "timestamp" TIMESTAMP NOT NULL,
    "store_id" BYTEA NOT NULL,
    "total_price" DOUBLE PRECISION NOT NULL,
    "payment_type" CHAR(4) NOT NULL,
    "opt: hash customer name" BYTEA NULL,
    "opt: hash card info" BYTEA NULL,
    PRIMARY KEY ("order_id"),
    FOREIGN KEY ("store_id") REFERENCES stores("store_id")
);

-- Creates products table
CREATE TABLE "products"(
    "product_id" BYTEA NOT NULL,
    "item_name" VARCHAR(255) NOT NULL,
    "item_size" VARCHAR(255) NOT NULL,
    "item_price" DOUBLE PRECISION NOT NULL,
    PRIMARY KEY ("product_id")
);

-- Creates orders_products table
CREATE TABLE "orders_products"(
    "order_id" BYTEA NOT NULL,
    "product_id" BYTEA NOT NULL,
    "quantity" INTEGER NOT NULL,
    PRIMARY KEY ("order_id", "product_id"),
    FOREIGN KEY ("order_id") REFERENCES orders("order_id"),
    FOREIGN KEY ("product_id") REFERENCES products("product_id")
);

-- Comments
COMMENT
ON COLUMN
    "orders"."order_id" IS 'Hash the concatenated result of string of values in a row as unique ID. Use SHA256(or 512).';
COMMENT
ON COLUMN
    "orders"."payment_type" IS 'char(4)';
COMMENT
ON COLUMN
    "orders"."opt: hash customer name" IS 'char(64)';
COMMENT
ON COLUMN
    "orders"."opt: hash card info" IS 'char(64)';
COMMENT
ON COLUMN
    "orders"."timestamp" IS 'Check pgsql timestamp formatting';
COMMENT
ON COLUMN
    "products"."product_id" IS 'Hash the concatenated result of string of values in a ​row as unique ID. Use SHA256(or 512)';
COMMENT
ON COLUMN
    "orders_products"."quantity" IS 'aggregate of item_count where order_id and product_id';