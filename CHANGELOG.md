# Stagehand Python Changelog

## 0.5.5

### Patch Changes

[#215](https://github.com/browserbase/stagehand-python/pull/215) [`cb35254`](https://github.com/browserbase/stagehand-python/commit/cb35254) Thanks @derekmeegan! - Fix ability to pass raw JSON to Extract schema
[#225](https://github.com/browserbase/stagehand-python/pull/225) [`b23e005`](https://github.com/browserbase/stagehand-python/commit/b23e005) Thanks @derekmeegan! - add local cua example, remove root model from types
[#218](https://github.com/browserbase/stagehand-python/pull/218) [`1a919ad`](https://github.com/browserbase/stagehand-python/commit/1a919ad) Thanks @derekmeegan! - Pass api_timeout param to Stagehand API correctly
[#223](https://github.com/browserbase/stagehand-python/pull/223) [`de7d883`](https://github.com/browserbase/stagehand-python/commit/de7d883) Thanks @derekmeegan! - Fix search, navigate, go back, and go forward for gemini cua agent
[#221](https://github.com/browserbase/stagehand-python/pull/221) [`da570a1`](https://github.com/browserbase/stagehand-python/commit/da570a1) Thanks @miguelg719! - Add support for Haiku 4.5 CUA

## 0.5.4

### Patch Changes

[#205](https://github.com/browserbase/stagehand-python/pull/205) [`3bcdd05`](https://github.com/browserbase/stagehand-python/commit/3bcdd05) Thanks @derekmeegan! - Make litellm client async
[#213](https://github.com/browserbase/stagehand-python/pull/213) [`1d0577d`](https://github.com/browserbase/stagehand-python/commit/1d0577d) Thanks @miguelg719! - Added support for Gemini Computer Use models

## 0.5.3

### Patch Changes

[#196](https://github.com/browserbase/stagehand-python/pull/196) [`93f5c97`](https://github.com/browserbase/stagehand-python/commit/93f5c97) Thanks @chrisreadsf, @miguelg719 and Derek Meegan! - remove duplicate project id if already passed to Stagehand
[#203](https://github.com/browserbase/stagehand-python/pull/203) [`82c6fed`](https://github.com/browserbase/stagehand-python/commit/82c6fed) Thanks @miguelg719! - Bump openai dependency version
[#198](https://github.com/browserbase/stagehand-python/pull/198) [`057b38b`](https://github.com/browserbase/stagehand-python/commit/057b38b) Thanks @Zach10za! - Fix draw_overlay on env:LOCAL

## 0.5.2

### Patch Changes

[#191](https://github.com/browserbase/stagehand-python/pull/191) [`7fb6a6f`](https://github.com/browserbase/stagehand-python/commit/7fb6a6f) Thanks @miguelg719! - Add support for custom base_url on api
[#185](https://github.com/browserbase/stagehand-python/pull/185) [`ec22cb9`](https://github.com/browserbase/stagehand-python/commit/ec22cb9) Thanks @filip-michalsky! - fix camelCase and snake_case return api extract schema mismatch

## 0.5.1

### Patch Changes

[#183](https://github.com/browserbase/stagehand-python/pull/183) [`6f72281`](https://github.com/browserbase/stagehand-python/commit/6f72281) Thanks @shubh24 and @miguelg719! - Fixing downloads behavior for use_api=false
[#132](https://github.com/browserbase/stagehand-python/pull/132) [`edc57ac`](https://github.com/browserbase/stagehand-python/commit/edc57ac) Thanks @sanveer-osahan and @miguelg719! - Add LLM customization support (eg. api_base)
[#179](https://github.com/browserbase/stagehand-python/pull/179) [`51ca053`](https://github.com/browserbase/stagehand-python/commit/51ca053) Thanks @miguelg719! - Fix max_steps parsing for agent execute options
[#176](https://github.com/browserbase/stagehand-python/pull/176) [`d95974a`](https://github.com/browserbase/stagehand-python/commit/d95974a) Thanks @miguelg719! - Fix stagehand.metrics on env:BROWSERBASE
[#88](https://github.com/browserbase/stagehand-python/pull/88) [`021c946`](https://github.com/browserbase/stagehand-python/commit/021c946) Thanks @filip-michalsky! - added regression tests
[#161](https://github.com/browserbase/stagehand-python/pull/161) [`f68e86c`](https://github.com/browserbase/stagehand-python/commit/f68e86c) Thanks @arunpatro, @miguelg719 and Filip Michalsky! - Multi-tab support
[#181](https://github.com/browserbase/stagehand-python/pull/181) [`1bef512`](https://github.com/browserbase/stagehand-python/commit/1bef512) Thanks @miguelg719! - Fix openai-litellm dependency bug
[#177](https://github.com/browserbase/stagehand-python/pull/177) [`36ba981`](https://github.com/browserbase/stagehand-python/commit/36ba981) Thanks @miguelg719! - Fix temperature setting for GPT-5 family of models
[#174](https://github.com/browserbase/stagehand-python/pull/174) [`2e3eb1a`](https://github.com/browserbase/stagehand-python/commit/2e3eb1a) Thanks @miguelg719! - Added frame_id_map to support multi-tab handling on API

## 0.5.0

### Minor Changes
[#167](https://github.com/browserbase/stagehand-python/pull/167) [`76669f0`](https://github.com/browserbase/stagehand-python/commit/76669f0) Thanks @miguelg719! - Enable access to iframes on api

### Patch Changes

[#168](https://github.com/browserbase/stagehand-python/pull/168) [`a7d8c5e`](https://github.com/browserbase/stagehand-python/commit/a7d8c5e) Thanks @miguelg719! - Patch issue with passing a created session_id to init on api mode
[#155](https://github.com/browserbase/stagehand-python/pull/155) [`8d55709`](https://github.com/browserbase/stagehand-python/commit/8d55709) Thanks @Zach10za! - Fix error in press_key act util function
[#158](https://github.com/browserbase/stagehand-python/pull/158) [`426df10`](https://github.com/browserbase/stagehand-python/commit/426df10) Thanks @miguelg719! - Fix parsing schema for extract with no arguments (full page extract)
[#166](https://github.com/browserbase/stagehand-python/pull/166) [`15fd40b`](https://github.com/browserbase/stagehand-python/commit/15fd40b) Thanks @filip-michalsky! - fix logging param name
[#159](https://github.com/browserbase/stagehand-python/pull/159) [`cd3dc7f`](https://github.com/browserbase/stagehand-python/commit/cd3dc7f) Thanks @tkattkat! - Add support for claude 4 sonnet in agent & remove all images but the last two from anthropic cua client

## 0.4.1

### Patch Changes

[#146](https://github.com/browserbase/stagehand-python/pull/146) [`d0983da`](https://github.com/browserbase/stagehand-python/commit/d0983da) Thanks @miguelg719 and @the-roaring! - Pass sdk version number to API for debugging
[#145](https://github.com/browserbase/stagehand-python/pull/145) [`0732268`](https://github.com/browserbase/stagehand-python/commit/0732268) Thanks @filip-michalsky! - relaxed rich to 13.7.0
[#152](https://github.com/browserbase/stagehand-python/pull/152) [`f888d81`](https://github.com/browserbase/stagehand-python/commit/f888d81) Thanks @filip-michalsky! - simple event loop timeout for strict event loops for async playwright (which has blocking start)
[#140](https://github.com/browserbase/stagehand-python/pull/140) [`5e70c8d`](https://github.com/browserbase/stagehand-python/commit/5e70c8d) Thanks @Zach10za! - Add support for handling OS-level dropdowns

## 0.4.0

### Minor Changes

[#127](https://github.com/browserbase/stagehand-python/pull/127) [`a2fee2c`](https://github.com/browserbase/stagehand-python/commit/a2fee2c) Thanks @the-roaring! - bump to unused version range

## 0.1.0

### Minor Changes

[#126](https://github.com/browserbase/stagehand-python/pull/126) [`5263553`](https://github.com/browserbase/stagehand-python/commit/5263553) Thanks @the-roaring! - bump minor version to fix publishing disparity

### Patch Changes

[#126](https://github.com/browserbase/stagehand-python/pull/126) [`5263553`](https://github.com/browserbase/stagehand-python/commit/5263553) Thanks @the-roaring! - start using pychangeset to track changes
