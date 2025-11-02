-- AI Automation Test System Database Schema
-- PostgreSQL Schema for test results, failures, and learning data

-- ============================================================
-- TEST MANAGEMENT TABLES
-- ============================================================

-- Test Plans
CREATE TABLE IF NOT EXISTS test_plans (
    plan_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    description TEXT,
    plan_type VARCHAR(50),  -- comprehensive, smoke, regression, stress
    total_tests INT NOT NULL DEFAULT 0,
    parallel_workers INT DEFAULT 5,
    status VARCHAR(50) DEFAULT 'pending',  -- pending, running, completed, failed
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_by VARCHAR(255),
    metadata JSONB  -- Additional configuration
);

CREATE INDEX idx_test_plans_status ON test_plans(status);
CREATE INDEX idx_test_plans_created_at ON test_plans(created_at);

-- Test Scenarios (within a test plan)
CREATE TABLE IF NOT EXISTS test_scenarios (
    scenario_id VARCHAR(255) PRIMARY KEY,
    plan_id VARCHAR(255) REFERENCES test_plans(plan_id) ON DELETE CASCADE,
    persona_type VARCHAR(100) NOT NULL,
    intent VARCHAR(100) NOT NULL,
    query_count INT NOT NULL DEFAULT 1,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_test_scenarios_plan_id ON test_scenarios(plan_id);
CREATE INDEX idx_test_scenarios_persona ON test_scenarios(persona_type);
CREATE INDEX idx_test_scenarios_intent ON test_scenarios(intent);

-- Test Cases (individual tests)
CREATE TABLE IF NOT EXISTS test_cases (
    test_id VARCHAR(255) PRIMARY KEY,
    scenario_id VARCHAR(255) REFERENCES test_scenarios(scenario_id) ON DELETE CASCADE,
    plan_id VARCHAR(255) REFERENCES test_plans(plan_id) ON DELETE CASCADE,
    persona_type VARCHAR(100) NOT NULL,
    intent VARCHAR(100) NOT NULL,
    query TEXT NOT NULL,
    expected_entities JSONB,
    difficulty VARCHAR(50),  -- easy, medium, hard
    tags TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_test_cases_scenario_id ON test_cases(scenario_id);
CREATE INDEX idx_test_cases_plan_id ON test_cases(plan_id);
CREATE INDEX idx_test_cases_intent ON test_cases(intent);
CREATE INDEX idx_test_cases_persona ON test_cases(persona_type);

-- ============================================================
-- TEST RESULTS TABLES
-- ============================================================

-- Test Results
CREATE TABLE IF NOT EXISTS test_results (
    result_id SERIAL PRIMARY KEY,
    test_id VARCHAR(255) REFERENCES test_cases(test_id) ON DELETE CASCADE,
    plan_id VARCHAR(255) REFERENCES test_plans(plan_id) ON DELETE CASCADE,

    -- Test execution info
    query TEXT NOT NULL,
    intent VARCHAR(100),
    persona_type VARCHAR(100),

    -- Response data
    response JSONB NOT NULL,
    detected_intent VARCHAR(100),
    extracted_entities JSONB,

    -- Evaluation scores
    accuracy_score DECIMAL(5,2),
    relevance_score DECIMAL(5,2),
    completeness_score DECIMAL(5,2),
    coherence_score DECIMAL(5,2),
    latency_score DECIMAL(5,2),
    overall_score DECIMAL(5,2),

    -- Execution metrics
    execution_time_ms DECIMAL(10,2),
    status VARCHAR(50) NOT NULL,  -- passed, failed, error
    error_message TEXT,

    -- Timestamps
    executed_at TIMESTAMP DEFAULT NOW(),

    -- Metadata
    metadata JSONB
);

CREATE INDEX idx_test_results_test_id ON test_results(test_id);
CREATE INDEX idx_test_results_plan_id ON test_results(plan_id);
CREATE INDEX idx_test_results_status ON test_results(status);
CREATE INDEX idx_test_results_overall_score ON test_results(overall_score);
CREATE INDEX idx_test_results_executed_at ON test_results(executed_at);

-- ============================================================
-- FAILURE TRACKING TABLES
-- ============================================================

-- Test Failures (detailed failure records)
CREATE TABLE IF NOT EXISTS test_failures (
    failure_id SERIAL PRIMARY KEY,
    test_id VARCHAR(255) REFERENCES test_cases(test_id) ON DELETE CASCADE,
    result_id INT REFERENCES test_results(result_id) ON DELETE CASCADE,

    -- Failure details
    failure_type VARCHAR(100) NOT NULL,  -- intent_mismatch, entity_extraction, low_quality, timeout, error
    query TEXT NOT NULL,
    expected_intent VARCHAR(100),
    actual_intent VARCHAR(100),
    expected_entities JSONB,
    actual_entities JSONB,
    response TEXT,

    -- Evaluation scores at failure
    accuracy_score DECIMAL(5,2),
    relevance_score DECIMAL(5,2),
    completeness_score DECIMAL(5,2),
    coherence_score DECIMAL(5,2),
    latency_score DECIMAL(5,2),
    overall_score DECIMAL(5,2),

    -- Root cause analysis
    root_cause TEXT,
    suspected_component VARCHAR(255),  -- orchestrator, db_gateway, rag_service, etc.

    -- Resolution tracking
    fixed BOOLEAN DEFAULT FALSE,
    fix_description TEXT,
    fix_commit_hash VARCHAR(255),
    fixed_at TIMESTAMP,
    fixed_by VARCHAR(255),

    -- Timestamps
    occurred_at TIMESTAMP DEFAULT NOW(),
    last_seen_at TIMESTAMP DEFAULT NOW(),
    occurrence_count INT DEFAULT 1,

    -- Metadata
    metadata JSONB
);

CREATE INDEX idx_test_failures_test_id ON test_failures(test_id);
CREATE INDEX idx_test_failures_failure_type ON test_failures(failure_type);
CREATE INDEX idx_test_failures_fixed ON test_failures(fixed);
CREATE INDEX idx_test_failures_occurred_at ON test_failures(occurred_at);
CREATE INDEX idx_test_failures_suspected_component ON test_failures(suspected_component);

-- ============================================================
-- PATTERN ANALYSIS TABLES
-- ============================================================

-- Failure Patterns (identified common patterns)
CREATE TABLE IF NOT EXISTS failure_patterns (
    pattern_id SERIAL PRIMARY KEY,
    pattern_type VARCHAR(100) NOT NULL,  -- entity_extraction, intent_detection, response_quality
    pattern_description TEXT NOT NULL,

    -- Pattern characteristics
    frequency INT DEFAULT 1,
    severity VARCHAR(50),  -- critical, high, medium, low
    examples JSONB,  -- Array of example failures
    affected_intents TEXT[],
    affected_personas TEXT[],

    -- Fix tracking
    suggested_fix TEXT,
    fix_applied BOOLEAN DEFAULT FALSE,
    fix_description TEXT,
    fix_commit_hash VARCHAR(255),

    -- Priority and status
    priority VARCHAR(50),  -- critical, high, medium, low
    status VARCHAR(50) DEFAULT 'open',  -- open, in_progress, fixed, wont_fix

    -- Timestamps
    first_detected_at TIMESTAMP DEFAULT NOW(),
    last_detected_at TIMESTAMP DEFAULT NOW(),
    fixed_at TIMESTAMP,

    -- Metadata
    metadata JSONB
);

CREATE INDEX idx_failure_patterns_pattern_type ON failure_patterns(pattern_type);
CREATE INDEX idx_failure_patterns_status ON failure_patterns(status);
CREATE INDEX idx_failure_patterns_priority ON failure_patterns(priority);
CREATE INDEX idx_failure_patterns_frequency ON failure_patterns(frequency);

-- ============================================================
-- CONTINUOUS IMPROVEMENT TABLES
-- ============================================================

-- Prompt Improvements
CREATE TABLE IF NOT EXISTS prompt_improvements (
    improvement_id SERIAL PRIMARY KEY,
    component VARCHAR(255) NOT NULL,  -- orchestrator, rag_service, classification, etc.
    prompt_type VARCHAR(100),  -- intent_detection, entity_extraction, response_generation

    -- Old vs New prompt
    old_prompt TEXT NOT NULL,
    new_prompt TEXT NOT NULL,
    change_description TEXT,

    -- A/B test results
    old_avg_score DECIMAL(5,2),
    new_avg_score DECIMAL(5,2),
    improvement_percentage DECIMAL(5,2),
    test_sample_size INT,

    -- Deployment status
    status VARCHAR(50) DEFAULT 'proposed',  -- proposed, testing, approved, deployed, reverted
    deployed_at TIMESTAMP,
    reverted_at TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255),

    -- Metadata
    metadata JSONB
);

CREATE INDEX idx_prompt_improvements_component ON prompt_improvements(component);
CREATE INDEX idx_prompt_improvements_status ON prompt_improvements(status);

-- Parameter Tuning History
CREATE TABLE IF NOT EXISTS parameter_tuning (
    tuning_id SERIAL PRIMARY KEY,
    component VARCHAR(255) NOT NULL,
    parameter_name VARCHAR(255) NOT NULL,

    -- Old vs New value
    old_value TEXT NOT NULL,
    new_value TEXT NOT NULL,

    -- Performance impact
    old_avg_score DECIMAL(5,2),
    new_avg_score DECIMAL(5,2),
    improvement_percentage DECIMAL(5,2),
    test_sample_size INT,

    -- Deployment status
    status VARCHAR(50) DEFAULT 'proposed',
    deployed_at TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255),

    -- Metadata
    metadata JSONB
);

CREATE INDEX idx_parameter_tuning_component ON parameter_tuning(component);
CREATE INDEX idx_parameter_tuning_parameter_name ON parameter_tuning(parameter_name);

-- ============================================================
-- COVERAGE TRACKING
-- ============================================================

-- Test Coverage Matrix
CREATE TABLE IF NOT EXISTS test_coverage (
    coverage_id SERIAL PRIMARY KEY,
    intent VARCHAR(100) NOT NULL,
    persona_type VARCHAR(100) NOT NULL,
    test_count INT DEFAULT 0,
    last_tested_at TIMESTAMP,
    average_score DECIMAL(5,2),
    pass_rate DECIMAL(5,2),

    UNIQUE(intent, persona_type)
);

CREATE INDEX idx_test_coverage_intent ON test_coverage(intent);
CREATE INDEX idx_test_coverage_persona ON test_coverage(persona_type);

-- ============================================================
-- VIEWS FOR ANALYTICS
-- ============================================================

-- Daily Test Summary
CREATE OR REPLACE VIEW daily_test_summary AS
SELECT
    DATE(executed_at) as test_date,
    COUNT(*) as total_tests,
    COUNT(*) FILTER (WHERE status = 'passed') as passed,
    COUNT(*) FILTER (WHERE status = 'failed') as failed,
    COUNT(*) FILTER (WHERE status = 'error') as errors,
    ROUND(AVG(overall_score), 2) as avg_score,
    ROUND(AVG(execution_time_ms), 2) as avg_execution_time_ms
FROM test_results
GROUP BY DATE(executed_at)
ORDER BY test_date DESC;

-- Failure Trends
CREATE OR REPLACE VIEW failure_trends AS
SELECT
    DATE(occurred_at) as failure_date,
    failure_type,
    COUNT(*) as count,
    COUNT(*) FILTER (WHERE fixed = true) as fixed_count
FROM test_failures
GROUP BY DATE(occurred_at), failure_type
ORDER BY failure_date DESC, count DESC;

-- Component Health
CREATE OR REPLACE VIEW component_health AS
SELECT
    suspected_component,
    COUNT(*) as failure_count,
    COUNT(*) FILTER (WHERE fixed = true) as fixed_count,
    ROUND(AVG(overall_score), 2) as avg_score,
    COUNT(*) FILTER (WHERE occurred_at > NOW() - INTERVAL '24 hours') as failures_last_24h
FROM test_failures
GROUP BY suspected_component
ORDER BY failure_count DESC;

-- Intent-Persona Performance
CREATE OR REPLACE VIEW intent_persona_performance AS
SELECT
    intent,
    persona_type,
    COUNT(*) as test_count,
    ROUND(AVG(overall_score), 2) as avg_score,
    COUNT(*) FILTER (WHERE status = 'passed') as passed,
    COUNT(*) FILTER (WHERE status = 'failed') as failed,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'passed') / COUNT(*), 2) as pass_rate
FROM test_results
GROUP BY intent, persona_type
ORDER BY avg_score DESC;

-- ============================================================
-- FUNCTIONS FOR COMMON OPERATIONS
-- ============================================================

-- Update test coverage matrix
CREATE OR REPLACE FUNCTION update_test_coverage()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO test_coverage (intent, persona_type, test_count, last_tested_at, average_score, pass_rate)
    VALUES (
        NEW.intent,
        NEW.persona_type,
        1,
        NEW.executed_at,
        NEW.overall_score,
        CASE WHEN NEW.status = 'passed' THEN 100.0 ELSE 0.0 END
    )
    ON CONFLICT (intent, persona_type)
    DO UPDATE SET
        test_count = test_coverage.test_count + 1,
        last_tested_at = NEW.executed_at,
        average_score = (test_coverage.average_score * test_coverage.test_count + NEW.overall_score) / (test_coverage.test_count + 1),
        pass_rate = (test_coverage.pass_rate * test_coverage.test_count + CASE WHEN NEW.status = 'passed' THEN 100.0 ELSE 0.0 END) / (test_coverage.test_count + 1);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update coverage on new test result
CREATE TRIGGER update_coverage_on_test_result
AFTER INSERT ON test_results
FOR EACH ROW
EXECUTE FUNCTION update_test_coverage();

-- ============================================================
-- SAMPLE DATA (for testing)
-- ============================================================

-- Insert sample test plan
INSERT INTO test_plans (plan_id, name, description, plan_type, total_tests, status)
VALUES ('sample_plan_001', 'Sample Comprehensive Test', 'Test plan for demonstration', 'comprehensive', 50, 'completed')
ON CONFLICT (plan_id) DO NOTHING;

COMMENT ON TABLE test_plans IS 'Test plans created by Test Orchestrator';
COMMENT ON TABLE test_scenarios IS 'Test scenarios within test plans (intent-persona combinations)';
COMMENT ON TABLE test_cases IS 'Individual test cases with queries';
COMMENT ON TABLE test_results IS 'Results of test executions with evaluation scores';
COMMENT ON TABLE test_failures IS 'Detailed failure records for learning';
COMMENT ON TABLE failure_patterns IS 'Identified common failure patterns';
COMMENT ON TABLE prompt_improvements IS 'History of prompt optimizations';
COMMENT ON TABLE parameter_tuning IS 'History of parameter tuning experiments';
COMMENT ON TABLE test_coverage IS 'Coverage matrix for intent-persona combinations';
