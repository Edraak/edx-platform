@shard_3
Feature: CMS Video Component Editor
  As a course author, I want to be able to create video components

  # 1
  Scenario: User can view Video metadata
    Given I have created a Video component
    And I edit the component
    Then I see the correct video settings and default values

  # 2
  # Safari has trouble saving values on Sauce
  @skip_safari
  Scenario: User can modify Video display name
    Given I have created a Video component
    And I edit the component
    And I open tab "Advanced"
    Then I can modify the display name
    And my video display name change is persisted on save

  # 3
  # Sauce Labs cannot delete cookies
  @skip_sauce
  Scenario: Captions are hidden when "transcript display" is false
    Given I have created a Video component with subtitles
    And I have set "transcript display" to False
    Then when I view the video it does not show the captions

  # 4
  # Sauce Labs cannot delete cookies
  @skip_sauce
  Scenario: Captions are shown when "transcript display" is true
    Given I have created a Video component with subtitles
    And I have set "transcript display" to True
    Then when I view the video it does show the captions

  # 5
  Scenario: Translations uploading works correctly
    Given I have created a Video component
    And I edit the component
    And I open tab "Advanced"
    And I upload transcript files:
      |lang_code|filename               |
      |zh       |chinese_transcripts.srt|
    And I save changes
    Then when I view the video it does show the captions
    And I see "好 各位同学" text in the captions
    And I edit the component
    And I open tab "Advanced"
    And I see translations for "zh"
    And I upload transcript files:
      |lang_code|filename             |
      |uk       |test_transcripts.srt |
    And I save changes
    Then when I view the video it does show the captions
    And I see "好 各位同学" text in the captions

  # 6
  Scenario: Translations downloading works correctly w/ preliminary saving
    Given I have created a Video component
    And I edit the component
    And I open tab "Advanced"
    And I upload transcript files:
      |lang_code|filename               |
      |uk       |test_transcripts.srt   |
      |zh       |chinese_transcripts.srt|
    And I save changes
    And I edit the component
    And I open tab "Advanced"
    And I see translations for "uk, zh"
    Then I can download transcript for "zh" language code, that contains text "好 各位同学"
    And I can download transcript for "uk" language code, that contains text "Hi, welcome to Edx."

  # 7
  Scenario: Translations downloading works correctly w/o preliminary saving
    Given I have created a Video component
    And I edit the component
    And I open tab "Advanced"
    And I upload transcript files:
      |lang_code|filename               |
      |uk       |test_transcripts.srt   |
      |zh       |chinese_transcripts.srt|
    Then I can download transcript for "zh" language code, that contains text "好 各位同学"
    And I can download transcript for "uk" language code, that contains text "Hi, welcome to Edx."

  # 8
  Scenario: Translations removing works correctly w/ preliminary saving
    Given I have created a Video component
    And I edit the component
    And I open tab "Advanced"
    And I upload transcript files:
      |lang_code|filename               |
      |uk       |test_transcripts.srt   |
      |zh       |chinese_transcripts.srt|
    And I save changes
    Then when I view the video it does show the captions
    And I see "Hi, welcome to Edx." text in the captions
    And I edit the component
    And I open tab "Advanced"
    And I see translations for "uk, zh"
    Then I remove translation for "uk" language code
    And I confirm prompt
    And I save changes
    Then when I view the video it does show the captions
    And I see "好 各位同学" text in the captions
    And I edit the component
    And I open tab "Advanced"
    And I see translations for "zh"
    Then I remove translation for "zh" language code
    And I confirm prompt
    And I save changes
    Then when I view the video it does not show the captions

  # 9
  Scenario: Translations removing works correctly w/o preliminary saving
    Given I have created a Video component
    And I edit the component
    And I open tab "Advanced"
    And I upload transcript files:
      |lang_code|filename               |
      |uk       |test_transcripts.srt   |
    And I see translations for "uk"
    Then I remove translation for "uk" language code
    And I confirm prompt
    And I save changes
    Then when I view the video it does not show the captions

  # 10
  Scenario: Translations clearing works correctly w/ preliminary saving
    Given I have created a Video component
    And I edit the component
    And I open tab "Advanced"
    And I upload transcript files:
      |lang_code|filename               |
      |uk       |test_transcripts.srt   |
      |zh       |chinese_transcripts.srt|
    And I save changes
    Then when I view the video it does show the captions
    And I see "Hi, welcome to Edx." text in the captions
    And I edit the component
    And I open tab "Advanced"
    And I see translations for "uk, zh"
    And I click button "Clear"
    And I confirm prompt
    And I save changes
    Then when I view the video it does not show the captions

  # 11
  Scenario: Translations clearing works correctly w/o preliminary saving
    Given I have created a Video component
    And I edit the component
    And I open tab "Advanced"
    And I upload transcript files:
      |lang_code|filename               |
      |uk       |test_transcripts.srt   |
      |zh       |chinese_transcripts.srt|
    And I click button "Clear"
    And I confirm prompt
    And I save changes
    Then when I view the video it does not show the captions

  # 12
  Scenario: Translations can be removed w/o prompt, if transcript file is not uploaded
    Given I have created a Video component
    And I edit the component
    And I open tab "Advanced"
    And I click button "Add"
    And I choose "zh" language code
    And I remove translation for "zh" language code
    Then I do not see translations

  # 13
  Scenario: Translations can be cleared w/o prompt, if transcript file is not uploaded
    Given I have created a Video component
    And I edit the component
    And I open tab "Advanced"
    And I click button "Add"
    And I choose "zh" language code
    And I click button "Clear"
    Then I do not see translations

  # 14
  Scenario: User cannot upload translations in sjson format
    Given I have created a Video component
    And I edit the component
    And I open tab "Advanced"
    And I click button "Add"
    And I choose "uk" language code
    And I try to upload transcript file "test_transcripts.sjson"
    Then I see validation error "Only SRT files can be uploaded. Please select a file ending in .srt to upload."
