# Sonar Reference

Sonar controls are Docker-template based and target-stack aware.

Generate templates into `.harness/sonar/`:

- `docker-compose.sonar.yml`
- `sonar-project.properties`

Supported stack detection:

- Node/TypeScript: `package.json`, `tsconfig.json`, `coverage/lcov.info`
- Python: `pyproject.toml`, `setup.py`, `requirements.txt`, `coverage.xml`
- Java Maven: `pom.xml`, `target/site/jacoco/jacoco.xml`
- Java Gradle: `build.gradle`, `build.gradle.kts`, `build/reports/jacoco/test/jacocoTestReport.xml`
- Go: `go.mod`, `coverage.out`
- .NET: `*.csproj`, `coverage.opencover.xml`
- Generic fallback: conservative `sonar.sources=.` exclusions

Policy:

- Template generation is safe.
- Docker image pulls, service startup, and scanner execution are approval-required.
- Use `SONAR_TOKEN` and `SONAR_HOST_URL` environment variables.
- Never write secrets to `.harness`.
- Record missing Docker, missing token, or scan failure as evidence or a harness gap.
