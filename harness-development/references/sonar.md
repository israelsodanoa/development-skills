# Sonar Reference

Sonar controls are Docker-based, target-stack aware, runtime verified, and fully local.

Harness init configures and starts SonarQube by default. A successful init must:

1. Generate stack-aware Sonar files.
2. Start the `sonarqube` Docker Compose service with forced authentication disabled for local anonymous analysis.
3. Poll `http://localhost:9000/api/system/status` or the configured port.
4. Record `status: running` in `.harness/sonar/sonar-config.json`.

Generate these files into `.harness/sonar/`:

- `docker-compose.sonar.yml`
- `sonar-project.properties`
- `.env.example`
- `sonar-config.json`

Supported stack detection:

- Node/TypeScript: `package.json`, `tsconfig.json`, `coverage/lcov.info`
- Python: `pyproject.toml`, `setup.py`, `requirements.txt`, `coverage.xml`
- Java Maven: `pom.xml`, `target/site/jacoco/jacoco.xml`
- Java Gradle: `build.gradle`, `build.gradle.kts`, `build/reports/jacoco/test/jacocoTestReport.xml`
- Go: `go.mod`, `coverage.out`
- .NET: `*.csproj`, `coverage.opencover.xml`
- Generic fallback: conservative `sonar.sources=.` exclusions

Policy:

- `init_project_harness.py` starts and verifies SonarQube unless `--skip-sonar` is passed.
- Docker image pulls, service startup, scanner execution, and shutdown are runtime operations and must be labeled in the command registry.
- Do not require host Sonar, host scanner, SonarCloud, or a manually created `SONAR_TOKEN`.
- Before scanning, use the Docker image's default local admin credentials to grant `anyone` local global `scan` and `provisioning` permissions, create the local project when needed, grant `anyone` project `user` and `scan` permissions, and do not persist credentials.
- Run required scans through `command_engine.py run --id quality.sonar.run --approved` so request state records closeout evidence.
- `quality.sonar.run` is required before every closeout and must fail when the quality gate fails.
- Runtime commands use a deterministic per-target Docker Compose project name to keep local containers and volumes isolated.
- Never write secrets to `.harness`.
- Record missing Docker, port conflicts, health timeouts, and scan failures in `sonar-config.json` and request evidence.
- Init may claim SonarQube is running only after the system API returns `UP`.
