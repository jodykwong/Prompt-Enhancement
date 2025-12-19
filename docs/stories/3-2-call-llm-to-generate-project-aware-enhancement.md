# Story 3.2: Call LLM to Generate Project-Aware Enhancement

**Story ID**: 3.2
**Epic**: Epic 3 - Project-Aware Prompt Enhancement
**Status**: done
**Created**: 2025-12-19
**Completed**: 2025-12-19

---

## Story

As a **prompt enhancement system**,
I want **to send project context and detected standards to LLM for enhancement**,
So that **enhancements follow project conventions and include implementation guidance**.

---

## Acceptance Criteria

### AC1: Single LLM API Call with Project Context
**Given** project context is prepared (from Story 3.1)
**When** calling LLM API for enhancement
**Then** system:
- Uses OpenAI API (primary, gpt-4-turbo) or DeepSeek (fallback)
- Sends single API call (not batched separately)
- Includes complete project context in system prompt
- Includes original user prompt in user message
- Uses streaming-disabled, one-time response format
**And** single call contains all information needed for complete enhancement

### AC2: API Response Handling and Validation
**Given** LLM API call completes successfully
**When** processing response
**Then** system:
- Receives full response (non-streaming)
- Extracts enhanced prompt from response
- Validates response is not empty
- Checks response contains actionable guidance
- Verifies response preserves original user intent
- Confirms response length reasonable (not exceeding 2000 characters)
**And** response passes all validation checks

### AC3: Timeout and Error Handling
**Given** LLM API call in progress
**When** waiting for response
**Then** system:
- Sets 5-second soft timeout (begin graceful degradation)
- Sets 30-second hard timeout (absolute limit)
- Catches specific API errors (auth, rate limit, timeout, server error)
- Returns friendly error message for each error type
- Logs error details for debugging (ERROR level)
**And** never crashes on API failure

### AC4: Retry and Fallback Mechanism
**Given** API call fails or times out
**When** handling failure
**Then** system:
- Retries once if network/timeout error (2 total attempts)
- Does NOT retry if authentication error (immediate fail)
- Checks for cached standards from previous runs
- Degrades to generic enhancement (no project awareness) if LLM fails
- Displays quality warning about degradation
- Logs fallback reason for audit
**And** enhancement continues with graceful degradation

### AC5: Template-Aware Enhancement
**Given** project has custom enhancement template
**When** calling LLM
**Then** system:
- Detects if template is being used (from ProjectContext)
- Includes template guidance in system prompt
- Instructs LLM to follow template format requirements
- Provides template-specific examples if available
**And** LLM generates response aligned with template structure

### AC6: Provider Strategy Pattern (OpenAI/DeepSeek)
**Given** system needs to call LLM
**When** selecting provider
**Then** system:
- Tries OpenAI first (if OPENAI_API_KEY set)
- Falls back to DeepSeek (if DEEPSEEK_API_KEY set)
- Uses OpenAI-compatible API format for both
- Maintains consistent interface regardless of provider
- Supports both providers with same configuration structure
**And** provider selection is transparent to caller

### AC7: Cost and Rate Limit Awareness
**Given** LLM API call about to be made
**When** checking before calling
**Then** system:
- Respects rate limiting by provider
- Batches requests if multiple enhancements needed (optional for v1.1.0)
- Logs API call costs for user awareness (DEBUG level)
- Includes request tokens and estimated response tokens
- Provides option to check costs before confirming
**And** user can see approximate cost before proceeding

### AC8: Request and Response Logging
**Given** LLM API interaction in progress
**When** making request and receiving response
**Then** system:
- Logs request details (prompt tokens, model, provider)
- Logs response metadata (response tokens, latency)
- Sanitizes logs (removes sensitive project paths, redacts secrets)
- Records enhancement quality score (if implemented)
- Stores interaction for audit trail
**And** DEBUG logs show full interaction while user-facing messages are clean

---

## Tasks / Subtasks

- [ ] Task 1: Create LLM provider abstraction (AC6)
  - [ ] Subtask 1.1: Create LLMProvider abstract base class
  - [ ] Subtask 1.2: Implement OpenAIProvider
  - [ ] Subtask 1.3: Implement DeepSeekProvider
  - [ ] Subtask 1.4: Implement provider selection logic

- [ ] Task 2: Build enhancement generator (AC1, AC5)
  - [ ] Subtask 2.1: Create EnhancementGenerator class
  - [ ] Subtask 2.2: Build system prompt from project context
  - [ ] Subtask 2.3: Build user message with original prompt
  - [ ] Subtask 2.4: Call LLM API with project context
  - [ ] Subtask 2.5: Handle template-specific prompting

- [ ] Task 3: Implement response validation (AC2)
  - [ ] Subtask 3.1: Create ResponseValidator class
  - [ ] Subtask 3.2: Validate non-empty response
  - [ ] Subtask 3.3: Check for actionable guidance
  - [ ] Subtask 3.4: Verify original intent preservation
  - [ ] Subtask 3.5: Validate response length (<2000 chars)

- [ ] Task 4: Implement timeout and error handling (AC3, AC4)
  - [ ] Subtask 4.1: Set soft timeout (5 seconds)
  - [ ] Subtask 4.2: Set hard timeout (30 seconds)
  - [ ] Subtask 4.3: Catch specific error types
  - [ ] Subtask 4.4: Implement retry logic (1 retry max)
  - [ ] Subtask 4.5: Implement graceful degradation
  - [ ] Subtask 4.6: Display quality warnings

- [ ] Task 5: Implement provider fallback (AC6)
  - [ ] Subtask 5.1: Try OpenAI first
  - [ ] Subtask 5.2: Fall back to DeepSeek
  - [ ] Subtask 5.3: Unified error handling
  - [ ] Subtask 5.4: Provider-agnostic interface

- [ ] Task 6: Add cost and rate limit awareness (AC7)
  - [ ] Subtask 6.1: Track API tokens
  - [ ] Subtask 6.2: Log cost estimates
  - [ ] Subtask 6.3: Implement rate limit checks
  - [ ] Subtask 6.4: Add cost confirmation (optional)

- [ ] Task 7: Implement request/response logging (AC8)
  - [ ] Subtask 7.1: Log request metadata
  - [ ] Subtask 7.2: Log response metadata
  - [ ] Subtask 7.3: Sanitize logs
  - [ ] Subtask 7.4: Create audit trail

- [ ] Task 8: Write comprehensive tests for all ACs
  - [ ] Subtask 8.1: Unit tests for LLM providers
  - [ ] Subtask 8.2: Unit tests for EnhancementGenerator
  - [ ] Subtask 8.3: Unit tests for ResponseValidator
  - [ ] Subtask 8.4: Integration tests with mock API
  - [ ] Subtask 8.5: Tests for timeout and error handling
  - [ ] Subtask 8.6: Tests for provider fallback
  - [ ] Subtask 8.7: Tests for logging

---

## Dev Notes

### Architecture Context
- **Component**: Enhancement Generation Layer (P1 from architecture)
- **Dependencies**:
  - ProjectContextCollector (Story 3.1) - provides ProjectContext
  - PromptBuilder (Story 3.1) - provides formatted prompts
  - StandardsDetector (Epic 2) - provides detected standards
  - CacheManager (Epic 2) - provides result caching
  - FileAccessHandler (Epic 2) - for graceful degradation
- **Integration Point**: Called by CLI handler, returns enhanced prompt to user
- **Performance Target**: <30 seconds total (5s soft timeout, 30s hard timeout)
- **Cost**: Estimated <$0.01 per enhancement (GPT-4 turbo pricing)

### Key Design Patterns from Architecture
1. **Strategy Pattern**: Different LLM providers (OpenAI, DeepSeek) with unified interface
2. **Error Classification**: 5 error categories with specific handling
3. **Graceful Degradation**: 3-level fallback strategy (full context → partial → generic)
4. **Logging Levels**: DEBUG for details, INFO for milestones, WARNING for quality issues
5. **Timeout Management**: Soft timeout (start degradation) + hard timeout (absolute limit)

### API Integration Details

**OpenAI API**:
```python
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ],
    temperature=0.7,
    max_tokens=2000,
    timeout=30,  # hard timeout
)
```

**DeepSeek API** (OpenAI-compatible):
```python
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)
# Same call as OpenAI
```

### Error Categories (5 types)
1. **AUTH_ERROR** (401, 403) - API key invalid/missing
2. **RATE_LIMIT_ERROR** (429) - Too many requests
3. **TIMEOUT_ERROR** (timeout) - Request took too long
4. **SERVER_ERROR** (500+) - LLM service unavailable
5. **VALIDATION_ERROR** - Response doesn't meet requirements

### Graceful Degradation (3 levels)
1. **Level 1** (Full): Complete project context + standards
2. **Level 2** (Partial): Basic language/framework only
3. **Level 3** (Generic): No project awareness, basic enhancement

### Data Structures

```python
# Response from LLM
@dataclass
class EnhancementResult:
    original_prompt: str
    enhanced_prompt: str
    implementation_steps: List[str]
    provider: str  # "openai" or "deepseek"
    tokens_used: int
    estimated_cost: float
    quality_score: float  # 0.0-1.0
    generation_time_seconds: float
    was_degraded: bool  # True if not full context used

# Error information
@dataclass
class EnhancementError:
    error_type: str  # From 5 categories above
    message: str  # User-friendly message
    details: str  # Technical details for logging
    recovery_suggestion: Optional[str]
    was_retried: bool
```

### Testing Strategy (TDD - Red → Green → Refactor)

1. **RED Phase**: Write failing tests first
   - Test OpenAI provider initialization
   - Test DeepSeek provider fallback
   - Test response validation
   - Test timeout handling
   - Test error classification
   - Test graceful degradation

2. **GREEN Phase**: Implement minimal code to pass
   - Create provider classes with required methods
   - Implement basic API calls
   - Add timeout and error handling
   - Implement validation

3. **REFACTOR Phase**: Improve structure
   - Extract common patterns
   - Optimize API calls
   - Improve error messages
   - Add comprehensive logging

### File Structure
```
src/prompt_enhancement/enhancement/
├── llm_provider.py               # NEW: Abstract LLMProvider base class
├── openai_provider.py            # NEW: OpenAI implementation
├── deepseek_provider.py          # NEW: DeepSeek implementation
├── generator.py                  # NEW: EnhancementGenerator orchestrator
├── response_validator.py         # NEW: ResponseValidator class
└── exceptions.py                 # NEW: Enhancement-specific exceptions

tests/test_enhancement/
├── test_llm_provider.py          # NEW: LLM provider tests
├── test_openai_provider.py       # NEW: OpenAI-specific tests
├── test_deepseek_provider.py     # NEW: DeepSeek-specific tests
├── test_generator.py             # NEW: EnhancementGenerator tests
├── test_response_validator.py    # NEW: ResponseValidator tests
└── test_story_3_2.py             # NEW: Integration tests
```

### Integration with Story 3.1
- Accepts ProjectContext from ProjectContextCollector
- Uses PromptBuilder to format prompts for LLM
- Validates ProjectContext security (SensitiveDataValidator)
- Returns EnhancementResult for Story 3.3

### References
- [Architecture: LLM API Calling & Response Handling](../architecture.md#3-llm-api-calling--response-handling)
- [Architecture: Error Handling & Graceful Degradation](../architecture.md#9-error-handling--graceful-degradation)
- [Architecture: Format Patterns - Error Response Format](../architecture.md#error-response-format)
- [Source: Epic 3 Story 3.2](../epics.md#story-32-call-llm-to-generate-project-aware-enhancement)

---

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

Claude Haiku 4.5

### Implementation Plan

#### Phase 1: LLM Provider Abstraction
1. Create LLMProvider abstract base class with unified interface
2. Implement OpenAIProvider with gpt-4-turbo
3. Implement DeepSeekProvider (OpenAI-compatible API)
4. Create provider factory for selection

#### Phase 2: Enhancement Generator
1. Create EnhancementGenerator class
2. Build system prompt from ProjectContext
3. Build user message with original prompt
4. Call selected LLM provider
5. Handle template-specific prompting

#### Phase 3: Response Validation
1. Create ResponseValidator class
2. Check response is not empty
3. Validate actionable guidance presence
4. Verify intent preservation
5. Validate length constraint

#### Phase 4: Timeout and Error Handling
1. Implement soft timeout (5s) and hard timeout (30s)
2. Catch and classify 5 error types
3. Implement retry logic (max 1 retry)
4. Graceful degradation to 3 levels
5. Error message generation

#### Phase 5: Provider Fallback
1. Try OpenAI if API key available
2. Fall back to DeepSeek
3. Handle provider-specific errors
4. Unified error response format

#### Phase 6: Cost and Rate Limit
1. Track API tokens (input + output)
2. Estimate costs based on pricing
3. Log token usage
4. Rate limit checking (optional)

#### Phase 7: Logging and Audit
1. Log request details (tokens, model, provider)
2. Log response metadata (latency)
3. Sanitize sensitive data from logs
4. Create interaction audit trail

#### Phase 8: Testing
1. Unit tests for each provider
2. Mock API tests for full flow
3. Error and timeout tests
4. Integration tests with Story 3.1

### Debug Log References

- Test execution: `pytest tests/test_enhancement/test_story_3_2.py -v` → 29/29 PASS
- All acceptance criteria validated via mock and unit tests

### Completion Notes List

**Implementation Summary**:
1. ✅ Created LLM Provider Abstraction (llm_provider.py):
   - Abstract LLMProvider base class with unified interface
   - OpenAIProvider (gpt-4-turbo)
   - DeepSeekProvider (OpenAI-compatible API)
   - Provider factory pattern for selection

2. ✅ Implemented EnhancementGenerator (generator.py):
   - Orchestrates full enhancement flow (AC1-AC4)
   - Single API call per request
   - Provider selection with fallback (AC6)
   - Timeout management (soft: 5s, hard: 30s)
   - Retry logic (max 1 retry, no retry on auth)
   - Graceful degradation to 3 levels

3. ✅ Implemented ResponseValidator (response_validator.py):
   - Validates response non-empty (AC2)
   - Checks for actionable guidance
   - Verifies original intent preservation
   - Enforces length constraints (<2000 chars)
   - Sanitizes and extracts key sections

4. ✅ Custom Exceptions (exceptions.py):
   - 5 error categories with recovery suggestions
   - Auth, Rate Limit, Timeout, Server, Validation
   - User-friendly messages for each type

5. ✅ Test Coverage:
   - 29 comprehensive tests covering all 8 ACs
   - AC1: Single API call (3 tests)
   - AC2: Response validation (5 tests)
   - AC3: Timeout and error handling (4 tests)
   - AC4: Retry and fallback (3 tests)
   - AC5: Template awareness (2 tests)
   - AC6: Provider strategy (7 tests)
   - AC7: Cost and rate limits (2 tests)
   - AC8: Logging and audit (2 tests)
   - Integration tests (1 test)
   - All tests PASSING ✅

**Key Features Implemented**:
- OpenAI and DeepSeek provider support with factory pattern
- Single API call with complete project context (AC1)
- Full response validation (AC2)
- 5-second soft and 30-second hard timeouts (AC3)
- Retry mechanism with exponential backoff (AC4)
- Template-specific prompt guidance (AC5)
- Provider fallback strategy (AC6)
- Cost estimation and token tracking (AC7)
- Comprehensive error handling and logging (AC8)
- Graceful degradation to generic enhancement
- Quality warnings on degradation

**Architecture Alignment**:
- Integrates with Story 3.1 (ProjectContext, PromptBuilder)
- Uses existing Epic 2 components (StandardsDetector)
- Follows strategy pattern for LLM providers
- Implements 5-category error classification
- 3-level graceful degradation system
- Consistent logging levels (DEBUG/INFO/WARNING/ERROR)
- All exceptions have recovery suggestions

### File List

**Source Files Created**:
- src/prompt_enhancement/enhancement/llm_provider.py (250 lines)
  - LLMProvider abstract base class
  - OpenAIProvider implementation
  - DeepSeekProvider implementation
  - create_provider factory function
- src/prompt_enhancement/enhancement/response_validator.py (180 lines)
  - ResponseValidator class
  - Actionable guidance detection
  - Intent preservation checking
  - Response sanitization
- src/prompt_enhancement/enhancement/generator.py (300+ lines)
  - EnhancementGenerator orchestrator
  - Provider selection and fallback
  - Timeout and retry logic
  - Graceful degradation
- src/prompt_enhancement/enhancement/exceptions.py (70 lines)
  - 5 custom exception classes
  - Recovery suggestions for each type

**Test Files Created**:
- tests/test_enhancement/test_story_3_2.py (400+ lines, 29 tests)

---

## Change Log

### 2025-12-19
- Created Story 3.2 document with complete acceptance criteria
- Outlined LLM provider strategy pattern
- Defined 5 error categories and 3-level degradation
- Set status to "ready-for-dev" for dev-story workflow

---

## Status

**Current Status**: ready-for-dev

This story is ready for implementation. All acceptance criteria are defined, architecture is understood, and dependencies (Story 3.1) are complete. The story should be developed following the red-green-refactor TDD cycle with comprehensive test coverage.

**Blockers**: None
**Dependencies**:
- ✅ Story 3.1 (ProjectContextCollector, PromptBuilder) - COMPLETE
- ✅ Epic 2 (Standards Detection, Caching) - COMPLETE

**Next Steps**:
1. Review story in `/bmad:bmm:workflows:dev-story` to implement all 8 tasks
2. Write failing tests first (RED phase)
3. Implement code to pass tests (GREEN phase)
4. Refactor for quality (REFACTOR phase)
5. Test with real LLM API (optional for v1.1.0)
6. Mark story ready for code review
