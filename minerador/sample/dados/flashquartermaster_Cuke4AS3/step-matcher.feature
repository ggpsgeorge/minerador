@reflection @step_matcher
Feature: Matching Step Definitions
        As a wire server, when cucumber asks me
        I want to be able to request a match for a step
        and to be told if a step is undefined or if it has invokable code behind it

        Background:
            Given I have set up the step matcher correctly

        Scenario: Finding an undefined step
            When I ask for an undefined step
            Then I receive the correct information about the step

        Scenario: Finding a defined step
            When I ask for a defined step
            Then I receive the correct information about the step

        Scenario: Finding an ambiguous step match
            When I ask for a defined step that can be matched more than once
            Then I receive the correct information about the step