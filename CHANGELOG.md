# Changelog

## 3.19.0 (2026-03-27)

Full Changelog: [v3.18.0...v3.19.0](https://github.com/browserbase/stagehand-python/compare/v3.18.0...v3.19.0)

### Features

* **internal:** implement indices array format for query and form serialization ([b2cccf5](https://github.com/browserbase/stagehand-python/commit/b2cccf56bc7e99d7869b8ed9339956a9f160348a))

## 3.18.0 (2026-03-25)

Full Changelog: [v3.7.0...v3.18.0](https://github.com/browserbase/stagehand-python/compare/v3.7.0...v3.18.0)

### Features

* Add explicit SSE event names for local v3 streaming ([493abf4](https://github.com/browserbase/stagehand-python/commit/493abf4ee2023c3a88701c01bdd4bfdd1f4e0b63))
* Include LLM headers in ModelConfig ([b0df6bc](https://github.com/browserbase/stagehand-python/commit/b0df6bcddaa9dbf206dee0d97ee9e303d703530b))


### Chores

* **ci:** skip lint on metadata-only changes ([4049e44](https://github.com/browserbase/stagehand-python/commit/4049e44cb7855c62d2231c34c6211532860dfdbf))
* **internal:** update gitignore ([5acaa6f](https://github.com/browserbase/stagehand-python/commit/5acaa6f97a3fd926e3406c3af3504576a86a05bb))

## 3.7.0 (2026-03-23)

Full Changelog: [v3.6.0...v3.7.0](https://github.com/browserbase/stagehand-python/compare/v3.6.0...v3.7.0)

### Features

* [fix]: add `useSearch` & `toolTimeout` to stainless types ([0faf1df](https://github.com/browserbase/stagehand-python/commit/0faf1dfb3d6b98e727bf0c904e272da3857863e8))
* [STG-1607] Yield finished SSE event instead of silently dropping it ([0bba1e9](https://github.com/browserbase/stagehand-python/commit/0bba1e9c657cffbbe306a2bc6520ab2992295773))
* Add bedrock to provider enum in Zod schemas and OpenAPI spec ([5ace8c9](https://github.com/browserbase/stagehand-python/commit/5ace8c9ee306ff8cc09c258500c24b6b55e9562b))
* Add missing cdpHeaders field to v3 server openapi spec ([7c17bc2](https://github.com/browserbase/stagehand-python/commit/7c17bc237e604ae38ca6772deb02a378d5117f81))
* Revert broken finished SSE yield config ([21189cf](https://github.com/browserbase/stagehand-python/commit/21189cf82aab6b07caf9a322f28355279b2a3f45))
* variables for observe ([93ef310](https://github.com/browserbase/stagehand-python/commit/93ef31098a0cb2b4acfd157ae4c45cedc2f2e58c))


### Bug Fixes

* **deps:** bump minimum typing-extensions version ([c8cce20](https://github.com/browserbase/stagehand-python/commit/c8cce20e513c91cff638742df3f19c477aeab795))
* **pydantic:** do not pass `by_alias` unless set ([b045b1a](https://github.com/browserbase/stagehand-python/commit/b045b1ab4d93aed7de6388fe31e768470d080fd4))
* sanitize endpoint path params ([5201ec1](https://github.com/browserbase/stagehand-python/commit/5201ec149265832d89100c9c5292985e2e65c0f8))


### Chores

* **ci:** bump uv version ([84a841c](https://github.com/browserbase/stagehand-python/commit/84a841cd29648432d713f10b37a530e18942a3f0))
* **ci:** skip uploading artifacts on stainless-internal branches ([291b296](https://github.com/browserbase/stagehand-python/commit/291b296a33c5be942422946051925ad6c500679b))
* **internal:** tweak CI branches ([1d33bbf](https://github.com/browserbase/stagehand-python/commit/1d33bbf69c610c4627e31345d5ae65828dfcc483))

## 3.6.0 (2026-02-25)

Full Changelog: [v3.5.0...v3.6.0](https://github.com/browserbase/stagehand-python/compare/v3.5.0...v3.6.0)

### Features

* Add executionModel serialization to api client ([22dd688](https://github.com/browserbase/stagehand-python/commit/22dd68831f5b599dc070798bb991b349211631d9))
* **client:** add custom JSON encoder for extended type support ([f9017c8](https://github.com/browserbase/stagehand-python/commit/f9017c8fff8c58992739c6924ed6efbae552e027))
* randomize region used for evals, split out pnpm and turbo cache, veri… ([18b63b8](https://github.com/browserbase/stagehand-python/commit/18b63b82d8abd4769b1b4f4dd00d29e157cb27b7))


### Chores

* format all `api.md` files ([c22d22c](https://github.com/browserbase/stagehand-python/commit/c22d22cd79700c3c12462f20e3ebad54b925968f))
* **internal:** add request options to SSE classes ([93cdbe5](https://github.com/browserbase/stagehand-python/commit/93cdbe53bb17beab4c370ef5e9c42dc76ebd46e3))
* **internal:** bump dependencies ([92d8393](https://github.com/browserbase/stagehand-python/commit/92d83930190c30b1d4653b78eb2a6e8d28225fa5))
* **internal:** codegen related update ([aa3fbd4](https://github.com/browserbase/stagehand-python/commit/aa3fbd46cfd8e3ad4f4db6724c14d43db52564b6))
* **internal:** codegen related update ([555a9c4](https://github.com/browserbase/stagehand-python/commit/555a9c44a902a6735e585e09ed974d9a7915a6bb))
* **internal:** fix lint error on Python 3.14 ([b0df744](https://github.com/browserbase/stagehand-python/commit/b0df7441a5a50cc8933d3f0edbc46561219d9fba))
* **internal:** make `test_proxy_environment_variables` more resilient ([82890a6](https://github.com/browserbase/stagehand-python/commit/82890a681e470d54e266c7706b0ea774ed0dc369))
* **internal:** make `test_proxy_environment_variables` more resilient to env ([1dfcc4b](https://github.com/browserbase/stagehand-python/commit/1dfcc4bece375e9ed04704da0dc0e8fd94b0f185))
* **internal:** remove mock server code ([195d489](https://github.com/browserbase/stagehand-python/commit/195d48951c67b69463976328b286e2311ad3fc9a))
* sync repo ([0c9bb8c](https://github.com/browserbase/stagehand-python/commit/0c9bb8cb3b791bf8c60ad0065fed9ad16b912b8e))
* update mock server docs ([4e8e5cf](https://github.com/browserbase/stagehand-python/commit/4e8e5cf63fc76628f79204e7be78d6b3b335838c))

## 3.5.0 (2026-01-29)

Full Changelog: [v3.4.8...v3.5.0](https://github.com/browserbase/stagehand-python/compare/v3.4.8...v3.5.0)

### Features

* add auto-bedrock support based on bedrock/provider.model-name ([eaded9f](https://github.com/browserbase/stagehand-python/commit/eaded9ffb050c297b86223c333044d8c22dd3cf4))
* Update stainless.yml for project and publish settings ([f90c553](https://github.com/browserbase/stagehand-python/commit/f90c55378c03c18215d1cdc153f84d587e5048b0))


### Bug Fixes

* **docs:** fix mcp installation instructions for remote servers ([85f8584](https://github.com/browserbase/stagehand-python/commit/85f85840c9e9de4c0c1b07ec1ef41936788ea88b))


### Chores

* **internal:** version bump ([d227b02](https://github.com/browserbase/stagehand-python/commit/d227b0213aa729243fbc56d818a808536b98b191))
* update SDK settings ([879b799](https://github.com/browserbase/stagehand-python/commit/879b7990e8095ca106bf9553159d6c7a01936ec9))

## 3.4.8 (2026-01-27)

Full Changelog: [v3.4.7...v3.4.8](https://github.com/browserbase/stagehand-python/compare/v3.4.7...v3.4.8)

### Chores

* sync repo ([efaf774](https://github.com/browserbase/stagehand-python/commit/efaf774f0dbd93db8e15e5c3800d62dd7670006c))

## 3.4.7 (2026-01-15)

Full Changelog: [v3.4.6...v3.4.7](https://github.com/browserbase/stagehand-python/compare/v3.4.6...v3.4.7)

## 3.4.6 (2026-01-13)

Full Changelog: [v3.4.5...v3.4.6](https://github.com/browserbase/stagehand-python/compare/v3.4.5...v3.4.6)

### Chores

* remove duplicate .keep files for pypi publish step fix ([5235658](https://github.com/browserbase/stagehand-python/commit/5235658b9360362d70d9154a96b53fe69167101d))

## 3.4.5 (2026-01-13)

Full Changelog: [v3.4.4...v3.4.5](https://github.com/browserbase/stagehand-python/compare/v3.4.4...v3.4.5)

### Chores

* windows logging/build fix ([5ed0e5f](https://github.com/browserbase/stagehand-python/commit/5ed0e5f633082295b1ab17af9291d6efc863d25d))

## 3.4.4 (2026-01-13)

Full Changelog: [v3.4.3...v3.4.4](https://github.com/browserbase/stagehand-python/compare/v3.4.3...v3.4.4)

### Chores

* publish-pypi lint fix ([71abdc6](https://github.com/browserbase/stagehand-python/commit/71abdc6f805c95f42da7c74dde961209a58290e7))

## 3.4.3 (2026-01-13)

Full Changelog: [v3.4.2...v3.4.3](https://github.com/browserbase/stagehand-python/compare/v3.4.2...v3.4.3)

### Chores

* force-include SEA binaries in wheel ([301147c](https://github.com/browserbase/stagehand-python/commit/301147ce8f7fde3726e04efaaecfcdc5755b7683))

## 3.4.2 (2026-01-13)

Full Changelog: [v3.4.1...v3.4.2](https://github.com/browserbase/stagehand-python/compare/v3.4.1...v3.4.2)

### Chores

* sync repo ([2d4bd0a](https://github.com/browserbase/stagehand-python/commit/2d4bd0aee5a1f03ed09473a43f5607871f05c7ee))

## [3.4.1](https://github.com/browserbase/stagehand-python/compare/v0.4.0...v3.4.1) (2026-01-13)


### Documentation

* refresh README for release ([41926c7](https://github.com/browserbase/stagehand-python/commit/41926c77f9f8ffcca32c341a33d50dc731e1d84a))

## [0.4.0](https://github.com/browserbase/stagehand-python/compare/v0.3.1...v0.4.0) (2026-01-13)


### Features

* don't close new opened tabs ([#161](https://github.com/browserbase/stagehand-python/issues/161)) ([#169](https://github.com/browserbase/stagehand-python/issues/169)) ([f68e86c](https://github.com/browserbase/stagehand-python/commit/f68e86c90d9e5f30d2f447ada65cc711ac531baa))


### Bug Fixes

* active page context ([#251](https://github.com/browserbase/stagehand-python/issues/251)) ([d61e118](https://github.com/browserbase/stagehand-python/commit/d61e118ccc8845ac95e4579f6137a91abb004943))
* set injected Stagehand cursor position to fixed for correct viewport tracking ([#121](https://github.com/browserbase/stagehand-python/issues/121)) ([#122](https://github.com/browserbase/stagehand-python/issues/122)) ([93c16e3](https://github.com/browserbase/stagehand-python/commit/93c16e392d754227f9bec47ee9d9f26046bfb770))

## 0.3.1 (2026-01-13)

Full Changelog: [v0.3.0...v0.3.1](https://github.com/browserbase/stagehand-python/compare/v0.3.0...v0.3.1)

## 0.3.0 (2026-01-12)

Full Changelog: [v0.2.4...v0.3.0](https://github.com/browserbase/stagehand-python/compare/v0.2.4...v0.3.0)

### Features

* Removed requiring x-language and x-sdk-version from openapi spec ([618266f](https://github.com/browserbase/stagehand-python/commit/618266f3fe397a2d346fc1f3adaad225db443cdf))
* Using provider/model syntax in modelName examples within openapi spec ([98d8ab9](https://github.com/browserbase/stagehand-python/commit/98d8ab97cb1115b9cff7f6e831b7dfa98e27f15a))

## 0.2.4 (2026-01-07)

Full Changelog: [v0.2.3...v0.2.4](https://github.com/browserbase/stagehand-python/compare/v0.2.3...v0.2.4)

### Documentation

* update README with SDK version headers ([f7bd20f](https://github.com/browserbase/stagehand-python/commit/f7bd20f4f44ae2b74a27bd791fa7bed3721b645c))

## 0.2.3 (2026-01-07)

Full Changelog: [v0.2.2...v0.2.3](https://github.com/browserbase/stagehand-python/compare/v0.2.2...v0.2.3)

### Bug Fixes

* use macos-15-intel runner for darwin-x64 builds ([8e716fa](https://github.com/browserbase/stagehand-python/commit/8e716faccb3b3cb5a9622a4f524813f9a17b6f2d))

## 0.2.2 (2026-01-07)

Full Changelog: [v0.2.1...v0.2.2](https://github.com/browserbase/stagehand-python/compare/v0.2.1...v0.2.2)

### Bug Fixes

* correct binary names and update macOS runner in publish workflow ([c396aa3](https://github.com/browserbase/stagehand-python/commit/c396aa32d85d6b16acaed2bbdadd3e619a87aae6))

## 0.2.1 (2026-01-07)

Full Changelog: [v0.2.0...v0.2.1](https://github.com/browserbase/stagehand-python/compare/v0.2.0...v0.2.1)

### Bug Fixes

* specify pnpm version 9 in publish workflow ([f4fdb7a](https://github.com/browserbase/stagehand-python/commit/f4fdb7a36ab4aea1e3c5a3e1604322a92fc5bd3f))

## 0.2.0 (2026-01-06)

Full Changelog: [v0.1.0...v0.2.0](https://github.com/browserbase/stagehand-python/compare/v0.1.0...v0.2.0)

### Features

* Added optional param to force empty object ([b15e097](https://github.com/browserbase/stagehand-python/commit/b15e0976bc356e0ce09b331705ccd2b8805e1bfa))
* **api:** manual updates ([5a3f419](https://github.com/browserbase/stagehand-python/commit/5a3f419522d49d132c4a75bf310eef1d9695a5a4))


### Documentation

* prominently feature MCP server setup in root SDK readmes ([d5a8361](https://github.com/browserbase/stagehand-python/commit/d5a83610cd39ccdecc1825d67a56ab2835d9651f))

## 0.1.0 (2025-12-23)

Full Changelog: [v0.0.1...v0.1.0](https://github.com/browserbase/stagehand-python/compare/v0.0.1...v0.1.0)

### Features

* [STG-1053] [server] Use fastify-zod-openapi + zod v4 for openapi generation ([405c606](https://github.com/browserbase/stagehand-python/commit/405c6068de29f39d90882b31805cc2785c6b94e0))
* **api:** manual updates ([dde1e8b](https://github.com/browserbase/stagehand-python/commit/dde1e8b312f72179c416baaa8603c4a5da9ce706))
* **api:** manual updates ([577cea0](https://github.com/browserbase/stagehand-python/commit/577cea04ec2814b9ec70e5f18119292991e5b635))
* **api:** manual updates ([0cdb22b](https://github.com/browserbase/stagehand-python/commit/0cdb22be4350e78b49a2c90bb62fbf5fcc0d4a25))
* **api:** manual updates ([fcf7666](https://github.com/browserbase/stagehand-python/commit/fcf7666829c41b7892d708c430a1a16b3ea6097e))
* **api:** manual updates ([8590a04](https://github.com/browserbase/stagehand-python/commit/8590a048dbe8a82b8b298b7345b30b71876b6e10))
* **api:** manual updates ([8d1c5ae](https://github.com/browserbase/stagehand-python/commit/8d1c5ae737a481f22818a4adcaba162d015142ee))
* **api:** manual updates ([638e928](https://github.com/browserbase/stagehand-python/commit/638e92824408754dadebbffab7be6e5f14c0034c))
* **api:** manual updates ([13484f8](https://github.com/browserbase/stagehand-python/commit/13484f87d343a9b02d58027ab17114c07fda5220))
* **api:** manual updates ([722abc9](https://github.com/browserbase/stagehand-python/commit/722abc902c2d7210b6b8c35655b9a8dbd6433ee3))
* **api:** manual updates ([72aa8b8](https://github.com/browserbase/stagehand-python/commit/72aa8b8476bddf351364a1bf161454206eaea3ba))
* **api:** manual updates ([54f3289](https://github.com/browserbase/stagehand-python/commit/54f32894104f60ca81cad4797b19a86903f4ef73))
* **api:** manual updates ([9b9d548](https://github.com/browserbase/stagehand-python/commit/9b9d548fb1a4f8a489d4dd920399d2145f4bd3af))
* **api:** manual updates ([54fb057](https://github.com/browserbase/stagehand-python/commit/54fb05764ac58ad86e9ef4a96aefdda001839fc7))
* **api:** manual updates ([5efd001](https://github.com/browserbase/stagehand-python/commit/5efd001ad8e5dbcea9f5aa7dad31584ade9402ae))
* **api:** manual updates ([19a67fd](https://github.com/browserbase/stagehand-python/commit/19a67fd34a16a0acd72427862bcd0eafd6dab353))
* **api:** manual updates ([80413be](https://github.com/browserbase/stagehand-python/commit/80413be240dd2cdf8c0c95f3e47c5537fbeed017))
* **api:** manual updates ([585015c](https://github.com/browserbase/stagehand-python/commit/585015c998f014040086fd927d91949c7d153b86))
* **api:** manual updates ([f032352](https://github.com/browserbase/stagehand-python/commit/f032352d00c69dd94438500c0ced3a110a7cc521))
* **api:** manual updates ([2dcbe2d](https://github.com/browserbase/stagehand-python/commit/2dcbe2d88a8a35781d42e5bbdcebb44e0ba830dc))
* **api:** tweak branding and fix some config fields ([8526eb4](https://github.com/browserbase/stagehand-python/commit/8526eb4417d0f2b69397294b1aa3d4da5892f2d6))


### Bug Fixes

* use async_to_httpx_files in patch method ([77eb123](https://github.com/browserbase/stagehand-python/commit/77eb1234c04a9aa95cedddb15bef377d644f6c42))


### Chores

* **internal:** add `--fix` argument to lint script ([f7eefb4](https://github.com/browserbase/stagehand-python/commit/f7eefb45344f354cfbdbfa00505f0225ce1ad396))
* **internal:** add missing files argument to base client ([5c05e7b](https://github.com/browserbase/stagehand-python/commit/5c05e7b37ae9aff8e259cc3190998d7e259f0cef))
* speedup initial import ([5aafb83](https://github.com/browserbase/stagehand-python/commit/5aafb83959802f8d2a6d7544f115de28a6495d2e))
* update SDK settings ([b8d1cd3](https://github.com/browserbase/stagehand-python/commit/b8d1cd34b5ee9608e52ea009ff31b7a429cdec62))
* update SDK settings ([4c0b2c8](https://github.com/browserbase/stagehand-python/commit/4c0b2c8045935a5790b668e553c114d82550b85e))


### Documentation

* add more examples ([681e90f](https://github.com/browserbase/stagehand-python/commit/681e90f695f60d3b59ee017da3270bd344cf01f6))


### Refactors

* **internal:** switch from rye to uv ([0eba9d2](https://github.com/browserbase/stagehand-python/commit/0eba9d2e2ba2ff82a412adf06e80866e3dc4b7cb))
