"""Test schema validation and serialization for Stagehand Pydantic models"""

import pytest
from pydantic import BaseModel, ValidationError
from typing import Dict, Any

from stagehand.schemas import (
    ActOptions,
    ActResult,
    ExtractOptions,
    ExtractResult,
    ObserveOptions,
    ObserveResult,
    AgentConfig,
    AgentExecuteOptions,
    AgentExecuteResult,
    AgentProvider,
    DEFAULT_EXTRACT_SCHEMA
)


class TestStagehandBaseModel:
    """Test the base model functionality"""
    
    def test_camelcase_conversion(self):
        """Test that snake_case fields are converted to camelCase in serialization"""
        options = ActOptions(
            action="test action",
            model_name="gpt-4o",
            dom_settle_timeout_ms=5000,
            slow_dom_based_act=True
        )
        
        serialized = options.model_dump(by_alias=True)
        
        # Check that fields are converted to camelCase
        assert "modelName" in serialized
        assert "domSettleTimeoutMs" in serialized  
        assert "slowDomBasedAct" in serialized
        assert "model_name" not in serialized
        assert "dom_settle_timeout_ms" not in serialized
    
    def test_populate_by_name(self):
        """Test that fields can be accessed by both snake_case and camelCase"""
        options = ActOptions(action="test")
        
        # Should be able to access by snake_case name
        assert hasattr(options, "model_name")
        
        # Should also work with camelCase in construction
        options2 = ActOptions(action="test", modelName="gpt-4o")
        assert options2.model_name == "gpt-4o"


class TestActOptions:
    """Test ActOptions schema validation"""
    
    def test_valid_act_options(self):
        """Test creation with valid parameters"""
        options = ActOptions(
            action="click on the button",
            variables={"username": "testuser"},
            model_name="gpt-4o",
            slow_dom_based_act=False,
            dom_settle_timeout_ms=2000,
            timeout_ms=30000
        )
        
        assert options.action == "click on the button"
        assert options.variables == {"username": "testuser"}
        assert options.model_name == "gpt-4o"
        assert options.slow_dom_based_act is False
        assert options.dom_settle_timeout_ms == 2000
        assert options.timeout_ms == 30000
    
    def test_minimal_act_options(self):
        """Test creation with only required fields"""
        options = ActOptions(action="click button")
        
        assert options.action == "click button"
        assert options.variables is None
        assert options.model_name is None
        assert options.slow_dom_based_act is None
    
    def test_missing_action_raises_error(self):
        """Test that missing action field raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            ActOptions()
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("action",) for error in errors)
    
    def test_serialization_includes_all_fields(self):
        """Test that serialization includes all non-None fields"""
        options = ActOptions(
            action="test action",
            model_name="gpt-4o",
            timeout_ms=5000
        )
        
        serialized = options.model_dump(exclude_none=True, by_alias=True)
        
        assert "action" in serialized
        assert "modelName" in serialized
        assert "timeoutMs" in serialized
        assert "variables" not in serialized  # Should be excluded as it's None


class TestActResult:
    """Test ActResult schema validation"""
    
    def test_valid_act_result(self):
        """Test creation with valid parameters"""
        result = ActResult(
            success=True,
            message="Button clicked successfully",
            action="click on submit button"
        )
        
        assert result.success is True
        assert result.message == "Button clicked successfully"
        assert result.action == "click on submit button"
    
    def test_failed_action_result(self):
        """Test creation for failed action"""
        result = ActResult(
            success=False,
            message="Element not found",
            action="click on missing button"
        )
        
        assert result.success is False
        assert result.message == "Element not found"
    
    def test_missing_required_fields_raises_error(self):
        """Test that missing required fields raise validation errors"""
        with pytest.raises(ValidationError):
            ActResult(success=True)  # Missing message and action


class TestExtractOptions:
    """Test ExtractOptions schema validation"""
    
    def test_valid_extract_options_with_dict_schema(self):
        """Test creation with dictionary schema"""
        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "price": {"type": "number"}
            }
        }
        
        options = ExtractOptions(
            instruction="extract product information",
            schema_definition=schema,
            model_name="gpt-4o"
        )
        
        assert options.instruction == "extract product information"
        assert options.schema_definition == schema
        assert options.model_name == "gpt-4o"
    
    def test_pydantic_model_schema_serialization(self):
        """Test that Pydantic models are properly serialized to JSON schema"""
        class ProductSchema(BaseModel):
            title: str
            price: float
            description: str = None
        
        options = ExtractOptions(
            instruction="extract product",
            schema_definition=ProductSchema
        )
        
        serialized = options.model_dump(by_alias=True)
        schema_def = serialized["schemaDefinition"]
        
        # Should be a dict, not a Pydantic model
        assert isinstance(schema_def, dict)
        assert "properties" in schema_def
        assert "title" in schema_def["properties"]
        assert "price" in schema_def["properties"]
    
    def test_default_schema_used_when_none_provided(self):
        """Test that default schema is used when none provided"""
        options = ExtractOptions(instruction="extract text")
        
        assert options.schema_definition == DEFAULT_EXTRACT_SCHEMA
    
    def test_schema_reference_resolution(self):
        """Test that $ref references in schemas are resolved"""
        class NestedSchema(BaseModel):
            name: str
        
        class MainSchema(BaseModel):
            nested: NestedSchema
            items: list[NestedSchema]
        
        options = ExtractOptions(
            instruction="extract nested data",
            schema_definition=MainSchema
        )
        
        serialized = options.model_dump(by_alias=True)
        schema_def = serialized["schemaDefinition"]
        
        # Should not contain $ref after resolution
        schema_str = str(schema_def)
        assert "$ref" not in schema_str or "$defs" not in schema_str


class TestObserveOptions:
    """Test ObserveOptions schema validation"""
    
    def test_valid_observe_options(self):
        """Test creation with valid parameters"""
        options = ObserveOptions(
            instruction="find the search button",
            only_visible=True,
            model_name="gpt-4o-mini",
            return_action=True,
            draw_overlay=False
        )
        
        assert options.instruction == "find the search button"
        assert options.only_visible is True
        assert options.model_name == "gpt-4o-mini"
        assert options.return_action is True
        assert options.draw_overlay is False
    
    def test_minimal_observe_options(self):
        """Test creation with only required fields"""
        options = ObserveOptions(instruction="find button")
        
        assert options.instruction == "find button"
        assert options.only_visible is False  # Default value
        assert options.model_name is None
    
    def test_missing_instruction_raises_error(self):
        """Test that missing instruction raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            ObserveOptions()
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("instruction",) for error in errors)


class TestObserveResult:
    """Test ObserveResult schema validation"""
    
    def test_valid_observe_result(self):
        """Test creation with valid parameters"""
        result = ObserveResult(
            selector="#submit-btn",
            description="Submit button in form",
            backend_node_id=12345,
            method="click",
            arguments=[]
        )
        
        assert result.selector == "#submit-btn"
        assert result.description == "Submit button in form"
        assert result.backend_node_id == 12345
        assert result.method == "click"
        assert result.arguments == []
    
    def test_minimal_observe_result(self):
        """Test creation with only required fields"""
        result = ObserveResult(
            selector="button",
            description="A button element"
        )
        
        assert result.selector == "button"
        assert result.description == "A button element"
        assert result.backend_node_id is None
        assert result.method is None
        assert result.arguments is None
    
    def test_dictionary_access(self):
        """Test that ObserveResult supports dictionary-style access"""
        result = ObserveResult(
            selector="#test",
            description="test element",
            method="click"
        )
        
        # Should support dictionary-style access
        assert result["selector"] == "#test"
        assert result["description"] == "test element"
        assert result["method"] == "click"


class TestExtractResult:
    """Test ExtractResult schema validation"""
    
    def test_extract_result_allows_extra_fields(self):
        """Test that ExtractResult accepts extra fields based on schema"""
        result = ExtractResult(
            title="Product Title",
            price=99.99,
            description="Product description",
            custom_field="custom value"
        )
        
        assert result.title == "Product Title"
        assert result.price == 99.99
        assert result.description == "Product description"
        assert result.custom_field == "custom value"
    
    def test_dictionary_access(self):
        """Test that ExtractResult supports dictionary-style access"""
        result = ExtractResult(
            extraction="Some extracted text",
            title="Page Title"
        )
        
        assert result["extraction"] == "Some extracted text"
        assert result["title"] == "Page Title"
    
    def test_empty_extract_result(self):
        """Test creation of empty ExtractResult"""
        result = ExtractResult()
        
        # Should not raise an error
        assert isinstance(result, ExtractResult)


class TestAgentConfig:
    """Test AgentConfig schema validation"""
    
    def test_valid_agent_config(self):
        """Test creation with valid parameters"""
        config = AgentConfig(
            provider=AgentProvider.OPENAI,
            model="gpt-4o",
            instructions="You are a helpful web automation assistant",
            options={"apiKey": "test-key", "temperature": 0.7}
        )
        
        assert config.provider == AgentProvider.OPENAI
        assert config.model == "gpt-4o"
        assert config.instructions == "You are a helpful web automation assistant"
        assert config.options["apiKey"] == "test-key"
    
    def test_minimal_agent_config(self):
        """Test creation with minimal parameters"""
        config = AgentConfig()
        
        assert config.provider is None
        assert config.model is None
        assert config.instructions is None
        assert config.options is None
    
    def test_agent_provider_enum(self):
        """Test AgentProvider enum values"""
        assert AgentProvider.OPENAI == "openai"
        assert AgentProvider.ANTHROPIC == "anthropic"
        
        # Test using enum in config
        config = AgentConfig(provider=AgentProvider.ANTHROPIC)
        assert config.provider == "anthropic"


class TestAgentExecuteOptions:
    """Test AgentExecuteOptions schema validation"""
    
    def test_valid_execute_options(self):
        """Test creation with valid parameters"""
        options = AgentExecuteOptions(
            instruction="Book a flight to New York",
            max_steps=10,
            auto_screenshot=True,
            wait_between_actions=1000,
            context="User wants to travel next week"
        )
        
        assert options.instruction == "Book a flight to New York"
        assert options.max_steps == 10
        assert options.auto_screenshot is True
        assert options.wait_between_actions == 1000
        assert options.context == "User wants to travel next week"
    
    def test_minimal_execute_options(self):
        """Test creation with only required fields"""
        options = AgentExecuteOptions(instruction="Complete task")
        
        assert options.instruction == "Complete task"
        assert options.max_steps is None
        assert options.auto_screenshot is None
    
    def test_missing_instruction_raises_error(self):
        """Test that missing instruction raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            AgentExecuteOptions()
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("instruction",) for error in errors)


class TestAgentExecuteResult:
    """Test AgentExecuteResult schema validation"""
    
    def test_successful_agent_result(self):
        """Test creation of successful agent result"""
        actions = [
            {"type": "navigate", "url": "https://example.com"},
            {"type": "click", "selector": "#submit"}
        ]
        
        result = AgentExecuteResult(
            success=True,
            actions=actions,
            message="Task completed successfully",
            completed=True
        )
        
        assert result.success is True
        assert len(result.actions) == 2
        assert result.actions[0]["type"] == "navigate"
        assert result.message == "Task completed successfully"
        assert result.completed is True
    
    def test_failed_agent_result(self):
        """Test creation of failed agent result"""
        result = AgentExecuteResult(
            success=False,
            message="Task failed due to timeout",
            completed=False
        )
        
        assert result.success is False
        assert result.actions is None
        assert result.message == "Task failed due to timeout"
        assert result.completed is False
    
    def test_minimal_agent_result(self):
        """Test creation with only required fields"""
        result = AgentExecuteResult(success=True)
        
        assert result.success is True
        assert result.completed is False  # Default value
        assert result.actions is None
        assert result.message is None


class TestSchemaIntegration:
    """Test integration between different schemas"""
    
    def test_observe_result_can_be_used_in_act(self):
        """Test that ObserveResult can be passed to act operations"""
        observe_result = ObserveResult(
            selector="#button",
            description="Submit button",
            method="click",
            arguments=[]
        )
        
        # This should be valid for act operations
        assert observe_result.selector == "#button"
        assert observe_result.method == "click"
    
    def test_pydantic_model_in_extract_options(self):
        """Test using Pydantic model as schema in ExtractOptions"""
        class TestSchema(BaseModel):
            name: str
            age: int = None
        
        options = ExtractOptions(
            instruction="extract person info",
            schema_definition=TestSchema
        )
        
        # Should serialize properly
        serialized = options.model_dump(by_alias=True)
        assert isinstance(serialized["schemaDefinition"], dict)
    
    def test_model_dump_consistency(self):
        """Test that all models serialize consistently"""
        models = [
            ActOptions(action="test"),
            ObserveOptions(instruction="test"),
            ExtractOptions(instruction="test"),
            AgentConfig(),
            AgentExecuteOptions(instruction="test")
        ]
        
        for model in models:
            # Should not raise errors
            serialized = model.model_dump()
            assert isinstance(serialized, dict)
            
            # With aliases
            aliased = model.model_dump(by_alias=True)
            assert isinstance(aliased, dict)
            
            # Excluding None values
            without_none = model.model_dump(exclude_none=True)
            assert isinstance(without_none, dict) 