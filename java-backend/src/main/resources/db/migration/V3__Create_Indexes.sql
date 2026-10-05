CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_tier ON customers(tier);
CREATE INDEX IF NOT EXISTS idx_customers_created_at ON customers(created_at);
CREATE INDEX IF NOT EXISTS idx_tickets_customer_status_created ON tickets(customer_id,status,created_at);
CREATE INDEX IF NOT EXISTS idx_tickets_status_priority ON tickets(status,priority);
CREATE INDEX IF NOT EXISTS idx_chat_session_created ON chat_messages(session_id,created_at);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_invoices_customer_status ON invoices(customer_id,status);
