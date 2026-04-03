# Database Migration Plan: Legacy Monolith to Microservices

## Completed Work (from Agent A)
- users table: migrated to auth-service DB, added uuid primary key, backfilled from integer IDs, foreign key references updated
- products table: migrated to catalog-service DB, split blob column into structured fields (name, description, metadata jsonb), indexed on sku
- orders table: migrated to order-service DB, partitioned by created_at (monthly), added composite index on (user_id, status)

## Remaining Work

### 1. Inventory Table Migration to warehouse-service DB

#### 1.1 Prepare Mapping (Assuming products mapping exists from completed work)
```sql
-- Verify products mapping exists (created during products migration)
-- This table maps old integer product_id to new uuid product_id
\dt *product_id_map*  -- Should exist from products migration
```

#### 1.2 Create New Inventory Table in warehouse-service DB
```sql
CREATE TABLE warehouse_service.inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES catalog_service.products(id),
    warehouse_code VARCHAR(50) NOT NULL,
    qty_on_hand INTEGER NOT NULL CHECK (qty_on_hand >= 0),
    last_restock TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_inventory_product_id ON warehouse_service.inventory(product_id);
CREATE INDEX idx_inventory_warehouse_code ON warehouse_service.inventory(warehouse_code);
```

#### 1.3 Set Up Logical Replication for Zero-Downtime Cutover
```sql
-- On source database (legacy monolith):
CREATE PUBLICATION inventory_pub FOR TABLE legacy.inventory;

-- On target database (warehouse-service):
CREATE SUBSCRIPTION inventory_sub 
    CONNECTION 'host=source_host dbname=legacy user=replicator password=secret'
    PUBLICATION inventory_pub
    WITH (copy_data = false, create_slot = false);

-- Initial data sync (after subscription creation, enable copy_data)
ALTER SUBSCRIPTION inventory_sub SET (copy_data = true);
-- Wait for initial sync to complete
ALTER SUBSCRIPTION inventory_sub SET (copy_data = false);
```

#### 1.4 Data Migration with ID Translation
```sql
-- Insert data with translated IDs
INSERT INTO warehouse_service.inventory (
    product_id, warehouse_code, qty_on_hand, last_restock, created_at, updated_at
)
SELECT 
    pmap.new_uuid as product_id,
    i.warehouse_code,
    i.qty_on_hand,
    i.last_restock,
    i.created_at,
    i.updated_at
FROM legacy.inventory i
JOIN product_id_map pmap ON i.product_id = pmap.old_integer;
```

#### 1.5 Cutover Procedure
```sql
-- 1. Stop writes to legacy.inventory (application maintenance window)
-- 2. Wait for replication to catch up
-- 3. Switch application to read from warehouse_service.inventory
-- 4. Begin writing to warehouse_service.inventory (double-write period)
-- 5. Verify consistency
-- 6. Stop double-write, use only new table
```

#### 1.6 Rollback Plan
```sql
-- If issues detected:
-- 1. Resume writing to legacy.inventory
-- 2. Keep warehouse_service.inventory as read-only backup
-- 3. Investigate and fix
-- 4. Retry cutover when ready
```

### 2. Analytics Table Migration to analytics-service DB

#### 2.1 Prepare Mapping (Assuming users mapping exists from completed work)
```sql
-- Verify users mapping exists (created during users migration)
\dt *user_id_map*  -- Should exist from users migration
```

#### 2.2 Create Partitioned Analytics Table in analytics-service DB
```sql
-- Create main table with weekly partitioning
CREATE TABLE analytics_service.analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL,
    user_id UUID NOT NULL REFERENCES auth_service.users(id),
    payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Create index for common queries
CREATE INDEX idx_analytics_user_id ON analytics_service.analytics(user_id);
CREATE INDEX idx_analytics_event_type ON analytics_service.analytics(event_type);
CREATE INDEX idx_analytics_created_at ON analytics_service.analytics(created_at);

-- Create weekly partitions (example for last 4 weeks and future)
DO $$
DECLARE
    start_date DATE := DATE_TRUNC('week', CURRENT_DATE) - INTERVAL '4 weeks';
    end_date DATE := DATE_TRUNC('week', CURRENT_DATE) + INTERVAL '8 weeks';
    current_date DATE := start_date;
BEGIN
    WHILE current_date < end_date LOOP
        EXECUTE format(
            'CREATE TABLE analytics_service.analytics_%s PARTITION OF analytics_service.analytics
             FOR VALUES FROM (%L) TO (%L)',
            TO_CHAR(current_date, 'YYYY_IW'),
            current_date,
            current_date + INTERVAL '1 week'
        );
        current_date := current_date + INTERVAL '1 week';
    END LOOP;
END $$;
```

#### 2.3 Set Up Logical Replication for Zero-Downtime Cutover
```sql
-- On source database (legacy monolith):
CREATE PUBLICATION analytics_pub FOR TABLE legacy.analytics;

-- On target database (analytics-service):
CREATE SUBSCRIPTION analytics_sub 
    CONNECTION 'host=source_host dbname=legacy user=replicator password=secret'
    PUBLICATION analytics_pub
    WITH (copy_data = false, create_slot = false);

-- Initial data sync
ALTER SUBSCRIPTION analytics_sub SET (copy_data = true);
-- Wait for initial sync to complete
ALTER SUBSCRIPTION analytics_sub SET (copy_data = false);
```

#### 2.4 Data Migration with ID Translation (Batch Processing for 420M Rows)
```sql
-- Process in batches to avoid locks and manage resources
DO $$
DECLARE
    batch_size INTEGER := 10000;
    last_id BIGINT := 0;
    rows_inserted INTEGER;
BEGIN
    LOOP
        WITH batch AS (
            SELECT a.event_type, umap.new_uuid as user_id, a.payload, a.created_at
            FROM legacy.analytics a
            JOIN user_id_map umap ON a.user_id = umap.old_integer
            WHERE a.id > last_id
            ORDER BY a.id
            LIMIT batch_size
        )
        INSERT INTO analytics_service.analytics (event_type, user_id, payload, created_at)
        SELECT event_type, user_id, payload, created_at FROM batch
        RETURNING 1 INTO rows_inserted;

        GET DIAGNOSTICS last_id = ROW_COUNT;
        EXIT WHEN rows_inserted = 0;
        
        -- Commit each batch
        COMMIT;
    END LOOP;
END $$;
```

#### 2.5 Cutover Procedure
```sql
-- 1. Stop writes to legacy.analytics (application maintenance window)
-- 2. Wait for replication to catch up
-- 3. Switch application to read from analytics_service.analytics
-- 4. Begin writing to analytics_service.analytics (double-write period)
-- 5. Verify consistency (especially partition routing)
-- 6. Stop double-write, use only new table
```

#### 2.6 Rollback Plan
```sql
-- If issues detected:
-- 1. Resume writing to legacy.analytics
-- 2. Keep analytics_service.analytics as read-only backup
-- 3. Investigate and fix (check partition constraints, indexing)
-- 4. Retry cutover when ready
```

## General Constraints Addressed
- ✅ Zero downtime: Using logical replication with double-write cutover
- ✅ FK updates: Using mapping tables to translate integer IDs to UUIDs
- ✅ Rollback plans: Defined for each table
- ✅ Inventory constraint: Added CHECK (qty_on_hand >= 0)
- ✅ Analytics partitioning: Weekly partitions created for performance
- ✅ Columnar storage consideration: Not implemented as standard PostgreSQL doesn't have native columnar storage; would require extension like cstore_fdw or switching to columnar DB (which would be architectural decision beyond SQL migration)

## Verification Steps
1. Row counts match between source and target (within replication lag)
2. Sample data validation (ID translations correct)
3. Application functionality testing with new tables
4. Performance baseline comparison